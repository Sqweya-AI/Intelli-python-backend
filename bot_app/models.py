# bot_app/models.py
from django.db import models

class Analysis(models.Model):
    user_input = models.TextField()
    analysis_response = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Input: {self.user_input[:20]}... | Analysis: {self.analysis_response[:20]}..."


class ChatHistory(models.Model):
    sender_id = models.CharField(max_length=100)  # WhatsApp sender ID
    recipient_id = models.CharField(max_length=100)  # WhatsApp recipient ID
    chat_history = models.JSONField()  # Storing the chat history as a JSON object
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the chat history was created

    def __str__(self):
        return f"Chat history from {self.sender_id} to {self.recipient_id} on {self.created_at}"