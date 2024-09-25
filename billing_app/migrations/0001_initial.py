# Generated by Django 5.0.7 on 2024-07-18 23:38

import datetime
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^\\d{16}$', 'Card number must be 16 digits.')])),
                ('card_holder_name', models.CharField(max_length=255)),
                ('expiration_date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2024, 7, 18))])),
                ('cvv', models.CharField(max_length=3, validators=[django.core.validators.RegexValidator('^\\d{3}$', 'CVV must be 3 digits.')])),
                ('billing_address', models.TextField()),
                ('zip_code', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^\\d{5}$', 'Zip code must be 5 digits.')])),
                ('country', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
