# Generated by Django 5.0.3 on 2024-04-04 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_rename_customer_name_reservationmodel_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationmodel',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined')], default='pending', max_length=100),
        ),
    ]
