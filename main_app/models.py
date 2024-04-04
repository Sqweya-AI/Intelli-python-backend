# main_app/models.py
from django.db import models


reservation_status = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('declined', 'Declined'),
]

class ReservationModel(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    customer_phone = models.CharField(max_length=20)
    number_of_adult_guests = models.IntegerField()
    number_of_child_guests = models.IntegerField()
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    room_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=reservation_status, default='pending')
    def __str__(self):
        return self.first_name + ' ' + self.last_name