from django.db import models

# Create your models here.

class Waitlist(models.Model):
    email_address = models.EmailField(null=True, blank=True)
    company_name  = models.CharField(max_length=300, null=True, blank=True)
    phone_number  = models.CharField(max_length=300, null=True, blank=True)



