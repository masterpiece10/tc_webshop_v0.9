# Generated by Django 3.0.3 on 2020-02-23 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(default='Hong Kong', max_length=120),
        ),
    ]
