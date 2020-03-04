import math
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Sum, Avg, Count
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils import timezone

from carts.models import Cart
from ecommerce.utils import unique_order_id_generator

from analytics.utilis import get_last_month_data, get_month_data_range
from addresses.models import Address
from billing.models import BillingProfile
from products.models import Product
# Create your models here.

ORDER_STATUS_CHOICES= (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),

)
class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by("-updated", "-timestamp")

    def by_date(self):
        now = timezone.now() - timedelta(days=13)
        return self.filter(updated__day__gte=now.day)

    def get_breakdown_data(self):
        recent = self.recent().not_refunded()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.not_refunded().by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.totals_data()
        paid_cart_data = paid.cart_data()
        data = {
            'recent': recent,
            'recent_data': recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data,
            'paid_cart_data': paid_cart_data,
        }
        return data

    def by_week_range(self, weeks_ago=1, number_of_weeks=1):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7
        days_ago_end = days_ago_start - number_of_weeks * 7
        start_date = timezone.now() - timedelta(days=days_ago_start)
        end_date = timezone.now() - timedelta(days=days_ago_end)
        return self.by_range(start_date=start_date, end_date=end_date)

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def totals_data(self):
        return self.aggregate(Sum("total"), Avg("total"))

    def cart_data(self):
        return self.aggregate(Avg("cart__product__price"), Count("cart__product"))

    def not_refunded(self):
        return self.exclude(status='refunded')

    def by_request(self, request):
        my_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=my_profile)
    
    def not_created(self):
        return self.exclude(status='created')

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)
        
    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
                        billing_profile=billing_profile, 
                        cart=cart_obj, 
                        active=True,
                        status='created',
                        )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                        billing_profile=billing_profile, 
                        cart=cart_obj)
            created=True
        return obj, created

class Order(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.SET_NULL)
    order_id            = models.CharField(max_length=120, blank=True)
    billing_address     = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True, on_delete=models.SET_NULL)
    shipping_address    = models.ForeignKey(Address, null=True, related_name='billing_address', blank=True, on_delete=models.SET_NULL)
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20, default=5.99)
    total               = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20, default=0.00)
    active              = models.BooleanField(default=True)
    updated             = models.DateTimeField(auto_now=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)

    objects=OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == "refunded":
            return "Refunded Order"
        elif self.status == "shipped":
            return "Shipping"
      
        return "Shipping soon"
    

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([float(cart_total) + float(shipping_total)])
        formatted_total = format(new_total, '.2f')
        self.total = formatted_total
        self.save()
        return formatted_total

    def check_done(self):
        shipping_address_required = self.cart.is_digital
        shipping_done = False
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True

        billing_profile = self.billing_profile
        billing_address = self.billing_address
        total = self.total
        if billing_profile and billing_address and total > 0:
            return True
        return False
    
    def update_purchases(self):
        for p in self.cart.product.all():
            obj, created = ProductPurchase.objects.get_or_create(
                            order_id = self.order_id,
                            product = p,
                            billing_profile = self.billing_profile,
                            )
            # obj.refunded = False
            # obj.save()
            return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def mark_paid(self):
        if self.status != "paid":
            if self.check_done():
                self.status = "paid"
                self.save()
                self.update_purchases()
        return self.status


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:\
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)


pre_save.connect(pre_save_create_order_id, sender=Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count():
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order, sender=Order)
# create order_id

class ProductPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(refunded=False)

    def digital(self):
        return self.filter(product__is_digital = True)

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)

class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active().digital()
    
    def digital(self):
        return self.get_queryset().active()
    
    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def products_by_id(self, request):
        qs = self.by_request(request).digital()
        ids_ = [x.product.id for x in qs]
        return ids_

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        product_qs = Product.objects.filter(id__in=ids_).distinct()
        return product_qs

    def get_order(self, order_id):
        qs = Order.objects.all().filter(order_id=order_id)
        return qs

class  ProductPurchase(models.Model):
    order_id        = models.CharField(max_length=120, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, blank=True, null=True, on_delete=models.SET_NULL)
    product         = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    refunded        = models.BooleanField(default=False)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title 