# Generated by Django 3.0.3 on 2020-02-19 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0004_address_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]