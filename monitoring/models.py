from django.db import models
from appservice.models import ChatSession

class SentimentAnalysis(models.Model):
    chatsession = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, related_name='sentiments')
    sentiments  = models.JSONField()
    created_at  = models.DateTimeField(auto_now_add=True)