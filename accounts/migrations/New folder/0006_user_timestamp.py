# Generated by Django 3.0.3 on 2020-02-20 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200220_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timestamp',
            field=models.DateField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
    ]
