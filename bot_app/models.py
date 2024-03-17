# bot_app/models.py
from django.db import models

class Analysis(models.Model):
    user_input = models.TextField()
    analysis_response = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Input: {self.user_input[:20]}... | Analysis: {self.analysis_response[:20]}..."
