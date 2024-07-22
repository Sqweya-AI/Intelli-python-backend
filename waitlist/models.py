from django.db import models


class Waitlist(models.Model):
    email_address = models.EmailField(max_length=255)
    company_name  = models.CharField(max_length=255)
    phone_number  = models.CharField(max_length=255)

