from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager,
)
from django.db import models

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
    active          = models.BooleanField(default=True) # login permission
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
        return self.staff
    
    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class GuestEmail(models.Model):
    email       = models.EmailField(max_length=254)
    uddate      = models.DateField(auto_now=True)
    timestamp   = models.DateField(auto_now_add=True)
    active      = models.BooleanField(default=True)

    def __str__(self):
        return self.email