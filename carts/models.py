import math

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed, post_delete
from django.shortcuts import reverse

from products.models import Product, Variation

User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = self.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user        = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    subtotal    = models.DecimalField(blank=True,null=True, decimal_places=2, max_digits=20, default=0.00)
    total       = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20, default=0.00)
    featured    = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def is_digital(self):
        for item in self.cartitem_set.all():
            if item.product.is_digital:
                return False
        return True

        # qs = self.cartitem_set.all()
        # new_qs = qs.filter(is_digital=False)
        # if new_qs.exists():
        #     return False
        # return True
       
def post_save_cart_receiver(sender, instance, *args, **kwargs):
    pass   
    

post_save.connect(post_save_cart_receiver, sender=Cart)  

def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    products = instance.cartitem_set.all()
    total = 0
    for item in products:
        total += item.product.price * item.quantity
    if instance.subtotal != total:
        instance.subtotal = total
        instance.save()
    
    if instance.subtotal > 0:
        instance.total = float(instance.subtotal) * 1.08
        
    else:
        instance.total = 0
    

pre_save.connect(pre_save_cart_receiver, sender=Cart)

class CartItemQuerySet(models.query.QuerySet):
    def get_name(self, id):
        # qs = self.filter(id=id)
        
        return self.filter(id=id)[0].product

    

class CarItemManager(models.Manager):
    def get_queryset(self):
        return CartItemQuerySet(self.model, using=self._db)

    def get_product_name(self, id):
        return self.get_queryset().get_name(id)

class CartItem(models.Model):
    cart        = models.ForeignKey(Cart, null=True, blank=True, on_delete=models.CASCADE)
    product     = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    variation   = models.ManyToManyField(Variation, blank=True)
    quantity    = models.IntegerField(default=1)
    line_total  = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    notes       = models.TextField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    objects = CarItemManager()

    def __str__(self):
        try:
            return str(self.cart.pk)
        except:
            return self.product.title
    
    def get_absolute_url(self):
        return reverse("products:details", kwargs={"slug": self.product.slug})

