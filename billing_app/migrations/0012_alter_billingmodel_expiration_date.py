# Generated by Django 5.0.3 on 2024-04-06 08:46

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_app', '0011_alter_billingmodel_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingmodel',
            name='expiration_date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2024, 4, 6))]),
        ),
    ]
