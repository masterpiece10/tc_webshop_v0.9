# Generated by Django 3.0.3 on 2020-02-25 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0006_marketingpreference_code_400'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketingpreference',
            name='code_400_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
