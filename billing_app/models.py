from django.db import models
from auth_app.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from datetime import date

class BillingModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, validators=[RegexValidator(r'^\d{16}$', 'Card number must be 16 digits.')], blank=False, null=False)
    card_holder_name = models.CharField(max_length=255, blank=False, null=False)
    expiration_date = models.DateField(validators=[MinValueValidator(date.today())], blank=False, null=False)
    cvv = models.CharField(max_length=3, validators=[RegexValidator(r'^\d{3}$', 'CVV must be 3 digits.')], blank=False, null=False)
    billing_address = models.TextField(blank=False, null=False)
    zip_code = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{5}$', 'Zip code must be 5 digits.')], blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f'Billing Info for {self.user.username}'
