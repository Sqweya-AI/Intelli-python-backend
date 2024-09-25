from rest_framework import serializers
from appservice.serializers import ChatSessionListSerializer

class SentimentAnalysisSerializer(serializers.Serializer):
    chatsession = ChatSessionListSerializer()
    sentiments  = serializers.JSONField()
    created_at  = serializers.DateTimeField()
