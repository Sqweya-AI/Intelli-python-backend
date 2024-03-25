# dashboard_app/models.py
from django.db import models
from auth_app.models import User

class AgentModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    agent_role = models.ForeignKey('AgentRoleModel', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name} Agent role = {self.agent_role}"
    
class AgentRoleModel(models.Model):
    role = models.CharField(max_length=100)
    number_of_agents = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.role

class ReservationModel(models.Model):
    customer_name = models.CharField(max_length=100)
    date = models.DateTimeField()
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    def __str__(self):
        return self.customer_name

class ContactChannelModel(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class DashboardModel(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(ReservationModel, on_delete=models.CASCADE)
    def __str__(self):
        return f'User - {self.user.username} (Manager)'


class HotelSettingsModel(models.Model):
    hotel_name = models.CharField(max_length=255)
    min_advance_booking = models.PositiveIntegerField()
    max_advance_booking = models.PositiveIntegerField()
    hotel_capacity = models.PositiveIntegerField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    hotel_address = models.TextField()
    hotel_phone = models.CharField(max_length=20)
    hotel_email = models.EmailField()
    cancellation_policy = models.TextField(blank=True, null=True)
    default_currency = models.CharField(max_length=3)  # ISO 4217 currency code
    room_types = models.JSONField(blank=True, null=True) # JSON field to store room types and their configurations
    accepted_payment_methods = models.JSONField(blank=True, null=True) # JSON field to store payment methods and their configurations
    hotel_amenities = models.JSONField(blank=True, null=True) # JSON field to store hotel amenities and their configurations

    class Meta:
        verbose_name_plural = "Settings"
    
    def __str__(self):
        return self.hotel_name


class UserSettingsModel(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    notification_settings = models.JSONField(blank=True, null=True) # JSON field to store notification settings
    user_preferences = models.JSONField(blank=True, null=True) # JSON field to store user preferences

    class Meta:
        verbose_name_plural = "Settings"
    
    def __str__(self):
        return self.name
    

