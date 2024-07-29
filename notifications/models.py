from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from appservice.models import ChatSession
# Create your models here.

class Notification(models.Model):
    chatsession      = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='notifications')
    text             = models.TextField()
    escalated_events = models.JSONField()
    channel          = models.CharField(null=True, blank=True, default=None)
    created_at       = models.DateTimeField(auto_now_add=True)
    

# def notify_clients(instance):
#     message = f"{instance.text}"
#     from .views import event_queue  # Importing here to avoid circular import issues
#     event_queue.put(message)

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'events',
            {
                'type': 'send_event',
                'message': f'{instance.text}'
            }
        )