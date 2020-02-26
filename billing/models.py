from django.conf import settings

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from accounts.models import GuestEmail

import stripe

stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

# Create your models here.
User = settings.AUTH_USER_MODEL
class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user    
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(
                                                    user=user, email=user.email)
        # guest checkout: out reload payment stuff
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                                                    email=guest_email_obj.email)
        else:
            print('no billing')
            pass
        
        return obj, created

class BillingProfile(models.Model):
    user        = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email       = models.EmailField(unique=True, max_length=254)
    uddate      = models.DateField(auto_now=True)
    timestamp   = models.DateField(auto_now_add=True)
    active      = models.BooleanField(default=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)

    objects = BillingProfileManager()

    def __str__(self):
        return str(self.email)

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse('payment')


    @property
    def has_card(self):
        card_qs = self.get_cards()
        return card_qs.exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(default=True, active=True)
        if default_cards:
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()



def billling_profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        customer = stripe.Customer.create(
            email = instance.email
        )
        instance.customer_id = customer.id
        

pre_save.connect(billling_profile_created_receiver, sender=BillingProfile)

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)

class CardManager(models.Manager):
    def all(self, *args, **kwargs): # ModelKlass.objects.all() --> ModelKlass.objects.filter(active=True)
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            stripe_card_response = customer.sources.create(source=token)
            new_card = self.model(
                    billing_profile=billing_profile,
                    stripe_id = stripe_card_response.id,
                    brand = stripe_card_response.brand,
                    country = stripe_card_response.country,
                    exp_month = stripe_card_response.exp_month,
                    exp_year = stripe_card_response.exp_year,
                    last4 = stripe_card_response.last4
                )
            new_card.save()
            return new_card
        return None


class Card(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
    stripe_id           = models.CharField(max_length=120)
    brand               = models.CharField(max_length=120, null=True, blank=True)
    country             = models.CharField(max_length=20, null=True, blank=True)
    exp_month           = models.IntegerField(null=True, blank=True)
    exp_year            = models.IntegerField(null=True, blank=True)
    last4               = models.CharField(max_length=4, null=True, blank=True)
    default             = models.BooleanField(default=True)
    active              = models.BooleanField(default=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return self.brand + " " + self.last4

def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)

post_save.connect(new_card_post_save_receiver, sender=Card)

class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):
        print(order_obj)
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No cards available"
        description = "Your Order " + str(order_obj) + " was paid to TC Test Shop"
        
        #
        #  need ecxeptions for the following payments (CC faults, server faults, etc)
        #

        
        c = stripe.Charge.create(
                amount      = int(order_obj.total * 100),    #need to be in cents
                currency    = "hkd",
                customer    = billing_profile.customer_id,
                source      = card_obj.stripe_id,
                description = description,
                metadata    = {
                            "order_id": order_obj,
                            },
        )
        new_charge_obj = self.model(
            billing_profile     = billing_profile,
            stripe_id           = c.id,
            paid                = c.paid,
            refunded            = c.refunded,
            outcome             = c.outcome,
            outcome_type        = c.outcome['type'],
            seller_message      = c.outcome.get('seller_message'),
            risk_level          = c.outcome.get('risk_level'),

        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message


class Charge(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
    stripe_id           = models.CharField(max_length=120)
    paid                = models.BooleanField(default=False)
    refunded            = models.BooleanField(default=False)
    outcome             = models.TextField(null=True, blank=True)
    outcome_type        = models.CharField(max_length=120, null=True, blank=True)
    seller_message      = models.CharField(max_length=120, null=True, blank=True)
    risk_level          = models.CharField(max_length=120, null=True, blank=True)

    objects=ChargeManager()

    # def __str__(self):
    #     return self.billing_profile