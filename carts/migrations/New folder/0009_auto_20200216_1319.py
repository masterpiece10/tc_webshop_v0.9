# Generated by Django 3.0.3 on 2020-02-16 05:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_cart_total'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='price',
            new_name='subtotal',
        ),
    ]
