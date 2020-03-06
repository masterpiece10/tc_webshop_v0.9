# Generated by Django 3.0.3 on 2020-03-01 00:55

import django.core.files.storage
from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_productfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='D:\\Programming\\Python3\\web\\new-start\\protected_media'), upload_to=products.models.upload_product_file_loc),
        ),
    ]