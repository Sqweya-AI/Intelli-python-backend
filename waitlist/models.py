from django.db import models

# Create your models here.


class IntelliWaitList(models.Model):
    company_name  = models.CharField(max_length=300)
    email_address = models.EmailField(unique=True)
    phone_number  = models.CharField(max_length=300)
