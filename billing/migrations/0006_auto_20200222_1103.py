# Generated by Django 3.0.3 on 2020-02-22 03:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20200222_1100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='exp_Year',
            new_name='exp_year',
        ),
    ]