# dashboard_app/models.py
from django.db import models
from auth_app.models import User

class AgentModel(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.CharField(max_length=100, null=False, blank=False)
    agent_role = models.ForeignKey('AgentRoleModel', on_delete=models.CASCADE, null=False, blank=False)
    def __str__(self):
        return f"{self.name} Agent role = {self.agent_role}"

class AgentRoleModel(models.Model):
    role = models.CharField(max_length=100, null=False, blank=False)
    number_of_agents = models.IntegerField(null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.role

class ContactChannelModel(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return self.name

class DashboardModel(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    def __str__(self):
        return f'User - {self.user.username} (Manager)'

class HotelSettingsModel(models.Model):
    """
    Model to store hotel settings and configurations.
    """
    number_of_rooms = models.IntegerField(null=False, blank=False, default=0)
    company_name = models.CharField(max_length=255, null=False, blank=False)
    company_phone = models.CharField(max_length=20, null=False, blank=False)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    company_email = models.EmailField(null=False, blank=False)
    company_website = models.URLField(null=True, blank=True)
    company_bio = models.TextField(null=True, blank=True)
    check_in_time = models.CharField(max_length=100, null=True, blank=True)
    check_out_time = models.CharField(max_length=100, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager_field_on_hotel_setting')
    def __str__(self):
        return f"{self.company_name}' Settings"
    
class Hotel(models.Model):
    """
    Model to store information about a hotel or property.
    """
    company_name = models.CharField(max_length=255, null=False, blank=False)
    settings = models.ForeignKey(HotelSettingsModel, on_delete=models.CASCADE, related_name='hotel_settings')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_manager')
    def __str__(self):
        return f"{self.company_name}"

class UserSettingsModel(models.Model):
    """
    Model to store user settings and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_settings')
    email = models.EmailField(null=False, blank=False, default='example@email.com')
    phone = models.CharField(max_length=20, null=True, blank=True)
    notification_settings = models.JSONField(blank=True, null=True, help_text="JSON field to store notification settings")
    dark_mode_enabled = models.BooleanField(default=False, help_text="Whether the user has enabled dark mode")
    def __str__(self):
        return f"{self.user.email}'s settings"
