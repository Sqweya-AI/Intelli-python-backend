from django.db import models
from auth_app.models import User

class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    agent_role = models.ForeignKey('AgentRole', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name} Agent role = {self.agent_role}"
    
class AgentRole(models.Model):
    role = models.CharField(max_length=100)
    number_of_agents = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.role

class Reservation(models.Model):
    customer_name = models.CharField(max_length=100)
    date = models.DateTimeField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    def __str__(self):
        return self.customer_name

class ContactChannel(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class DashboardModel(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    def __str__(self):
        return f'User - {self.user.username} (Manager)'
    