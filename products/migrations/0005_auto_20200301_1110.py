# Generated by Django 3.0.3 on 2020-03-01 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20200301_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfile',
            name='free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productfile',
            name='user_required',
            field=models.BooleanField(default=False),
        ),
    ]