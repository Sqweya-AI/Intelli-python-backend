from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from appservice.models import ChatSession

import json 
# Create your models here.

class Notification(models.Model):
    connection_id    = models.CharField(max_length=300, null=True, default='NOAPPLICABLE')
    chatsession      = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='notifications')
    text             = models.TextField()
    escalated_events = models.JSONField()
    channel          = models.CharField(null=True, blank=True, default=None)
    created_at       = models.DateTimeField(auto_now_add=True)
    

    def __str__(self) -> str:
        return f"{self.id} - {self.connection_id} - {self.created_at}"


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        connection_channel = f"connection_{instance.connection_id}"
        async_to_sync(channel_layer.group_send)(
            connection_channel,
            {
                'type': 'send_event',
                'message': f'{instance.text}\ncustomer number : {instance.chatsession.customer_number} \ncustomer name : {instance.chatsession.customer_name}'
            }
        )


# @receiver(post_save, sender=Notification)
# def send_notification(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'events',
#             {
#                 'type': 'send_event',
#                 'message': f'{instance.text}\ncustomer number : {instance.chatsession.customer_number} \ncustomer name : {instance.chatsession.customer_name}'
#             }
#         )

    