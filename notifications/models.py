from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from appservice.models import ChatSession
# Create your models here.

class Notification(models.Model):
    chatsession      = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='notifications')
    text             = models.TextField()
    escalated_events = models.JSONField()
    channel          = models.CharField(null=True, blank=True, default=None)
    created_at       = models.DateTimeField(auto_now_add=True)
    

def notify_clients(instance):
    message = f"{instance.text}"
    from .views import event_queue  # Importing here to avoid circular import issues
    event_queue.put(message)

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        # Notify clients about the new object creation
        notify_clients(instance)