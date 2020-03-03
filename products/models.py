import random
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

from ecommerce.utils import unique_slug_generator, get_filename

# Create your models here.
def get_filename_ext(filename):
    base_name = os.path.basename(filename)
    name, ext = os.path.splitext(filename)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1,2318233231)
    name, ext = get_filename_ext(filename)
    final_filename = f"{new_filename}{ext}"
    return f"products/{final_filename}"

class ProductsQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)

    def search(self, q):
        lookups =   (Q(title__icontains=q) | 
                    Q(description__icontains=q) | 
                    Q(slug__icontains=q)|
                    Q(tag__title__icontains=q)
                    )
        return self.filter(lookups).distinct()

class ProductManager(models.Manager):
    def all(self):
        return self.get_queryset().active()

    def get_queryset(self):
        return ProductsQuerySet(self.model, using=self._db)

    def features(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self,q):
        return self.get_queryset().active().search(q)

class Product(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique=True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2, max_digits=20, default=1.00)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_digital      = models.BooleanField(default=False)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse('products:details', kwargs={'slug': self.slug})
    

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)

def upload_product_file_loc(instance, filename):
    slug = instance.product.slug
    id_ = instance.id
    if id_ is None:
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = f"product/{slug}/{id_}/"
    return location + filename



class ProductFile(models.Model):
    product         = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    name            = models.CharField(max_length=255, null=True, blank=True)
    file            = models.FileField(
                        upload_to=upload_product_file_loc, 
                        storage=FileSystemStorage(location=settings.PROTECTED_ROOT)
                        )
    free            = models.BooleanField(default=False)    # bought or free?
    user_required   = models.BooleanField(default=False)    # need user or not?

    def __str__(self):
        return str(self.file.name)

    @property
    def display_name(self):
        og_name = get_filename(self.file.name)
        if self.name:
            return self.name 
        return og_name

    def get_default_url(self):
        return self.product.get_absolute_url()

    def get_download_url(self):
        return reverse("products:download", kwargs={"slug": self.product.slug, "pk": self.pk})

