# Generated by Django 3.0.3 on 2020-03-06 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_address_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(blank=True, help_text='Shipping to? Who is it for?', max_length=120, null=True),
        ),
    ]
