# Generated by Django 3.0.3 on 2020-03-09 02:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_productimage_variation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
