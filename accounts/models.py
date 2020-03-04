from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager,
)
from django.utils import timezone
from django.urls import reverse

from ecommerce.utils import random_string_generator, unique_key_generator
from django.core.mail import send_mail
from django.template.loader import get_template

from random import randint
from datetime import timedelta

# send_mail(subject, message, from_email, recipient_list, html_message)

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User musst have email address")
        if not password:
            raise ValueError("User must have a password")
        if not first_name:
            raise ValueError("Please enter First Name")
        if not last_name:
            raise ValueError("Please enter Last Name")

        user_obj = self.model(
            email = self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self.db)
        return user_obj

    def create_staff_user(self, email, first_name, last_name, password=None):
        user_obj = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
            is_staff=True
        )
        return user_obj

    def create_superuser(self, email, first_name, last_name, password=None):
        user_obj = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user_obj


class User(AbstractBaseUser):
    email           = models.EmailField(unique=True, max_length=255)
    first_name      = models.CharField(max_length=255)
    last_name       = models.CharField(max_length=255)
    is_active       = models.BooleanField(default=True)
    staff           = models.BooleanField(default=False) # staff user not SU
    admin           = models.BooleanField(default=False) # superuser
    timestamp       = models.DateField(auto_now_add=True)


    USERNAME_FIELD  = 'email' #username
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return  True
        return self.staff
    
    @property
    def is_admin(self):
        return self.admin

    # @property
    # def is_active(self):
    #     return self.active

class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days = DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
                activated=False,
                forced_expired = False,
                ).filter(
                    timestamp__gt = start_range,
                    timestamp__lte = end_range,
                )
    


class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)
    
    def confirmable(self):
        return self.get_queryset().confirmable()
    
    def email_exists(self, email):
        return self.get_queryset().filter(
                Q(email=email) | 
                Q(user__email=email))\
                .filter(activated=False)
    

class EmailActivation(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    email           = models.EmailField()
    key             = models.CharField(max_length=120, null=True, blank=True)
    activated       = models.BooleanField(default=False)
    forced_expired  = models.BooleanField(default=False)
    expires         = models.IntegerField(default=7) # in days
    timestamp       = models.DateField(auto_now_add=True)
    update          = models.DateField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user = self.user
            user.is_active = True
            user.save()
            # singal for user just activated post_save
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False


    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', 'https://www.treasure-china.net')
                key_path = reverse("accounts:email-activate", kwargs={'key': self.key}) # reverse url
                path = f"{base_url}{key_path}"
                context = {
                    'path': path,
                    'email': self.email,
                }
                
                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = "1-Click Email Verification"
                
                sent_mail = send_mail(
                    subject,
                    txt_,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    recipient_list = [self.email],
                    html_message = html_,
                    fail_silently=False,
                )
                return sent_mail
        return False

def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation_email()

post_save.connect(post_save_user_create_receiver, sender=User)

class GuestEmail(models.Model):
    email       = models.EmailField(max_length=254)
    uddate      = models.DateField(auto_now=True)
    timestamp   = models.DateField(auto_now_add=True)
    active      = models.BooleanField(default=True)

    def __str__(self):
        return self.email