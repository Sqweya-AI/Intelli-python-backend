from django.db import models

from business.models import Business


class AppService(models.Model):
    business         = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True)
    phone_number_id  = models.CharField(max_length=300, unique=True)
    phone_number     = models.CharField(max_length=300, unique=True)
    app_secret       = models.CharField(max_length=300, unique=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    whatsapp_business_account_id = models.CharField(max_length=300, unique=True, null=True)



class ChatSession(models.Model):
    customer_number    = models.CharField(max_length=300, unique=True, null=True, blank=True)
    customer_name      = models.CharField(max_length=300, null=True, blank=True)
    is_handle_by_human = models.BooleanField(default=False)
    appservice         = models.ForeignKey(AppService, on_delete=models.SET_NULL, null=True, related_name='chatsessions')
    thread_id          = models.CharField(max_length=300, null=True, blank=True, unique=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)
    


class Message(models.Model):
    content     = models.TextField(null=True, blank=True)
    answer      = models.TextField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    sender      = models.CharField(max_length=20, choices=[('human', 'human'), ('ai', 'ai')], null=True, blank=True)
    chatsession = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, related_name='messages')

