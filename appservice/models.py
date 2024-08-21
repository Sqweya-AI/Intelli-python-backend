from django.db import models

from business.models import Business

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class AppService(models.Model):
    business         = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True)
    phone_number_id  = models.CharField(max_length=300, unique=True)
    phone_number     = models.CharField(max_length=300, unique=True)
    app_secret       = models.CharField(max_length=300, unique=True)
    access_token     = models.TextField(null=True, blank=True)
    assistant_id     = models.CharField(max_length=300, unique=True, null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    whatsapp_business_account_id = models.CharField(max_length=300, unique=True, null=True)

    def __str__(self) -> str:
        return self.phone_number + ' ' + str(self.business)



class ChatSession(models.Model):
    customer_number    = models.CharField(max_length=300, null=True, blank=True)
    customer_name      = models.CharField(max_length=300, null=True, blank=True)
    is_handle_by_human = models.BooleanField(default=False)
    appservice         = models.ForeignKey(AppService, on_delete=models.SET_NULL, null=True, related_name='chatsessions')
    thread_id          = models.CharField(max_length=300, null=True, blank=True, unique=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['customer_number', 'appservice']

    
    def __str__(self) -> str:
        return self.customer_name + ' ' + self.customer_number + ' ' + self.appservice.phone_number

class Message(models.Model):
    content     = models.TextField(null=True, blank=True)
    answer      = models.TextField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    sender      = models.CharField(max_length=20, choices=[('human', 'human'), ('ai', 'ai')], null=True, blank=True)
    chatsession = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, related_name='messages')

    def __str__(self) -> str:
        return f"{self.created_at} - {self.content}"


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    # print(f'chat_{instance.chatsession.customer_number}_{instance.chatsession.appservice.phone_number}')
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{instance.chatsession.customer_number}_{instance.chatsession.appservice.phone_number}',  # Assurez-vous que le groupe correspond à votre logique de gestion de sessions
            {
                'type': 'chat_message',
                'message': {
                    'id': instance.id,
                    'content': instance.content,
                    'answer': instance.answer,
                    'created_at': instance.created_at.isoformat(),
                    'sender': instance.sender,
                }
            }
        )
