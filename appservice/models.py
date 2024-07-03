from django.db import models

from business.models import Business


class AppService(models.Model):
    business         = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True)
    phone_number_id  = models.CharField(max_length=300, unique=True)
    meta_app_id      = models.CharField(max_length=300, unique=True)
    phone_number     = models.CharField(max_length=300, unique=True)
    app_secret       = models.UUIDField(unique=True)
    created_at       = models.DateTimeField(auto_now_add=True)




class ChatSession(models.Model):
    customer_number    = models.CharField(max_length=300, unique=True)
    is_handle_by_human = models.BooleanField(default=False)
    appservice         = models.ForeignKey(AppService, on_delete=models.SET_NULL, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)
    


class Message(models.Model):
    content     = models.TextField()
    answer      = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    chatsession = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True)




