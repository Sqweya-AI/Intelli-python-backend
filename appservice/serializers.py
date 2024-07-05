from rest_framework import serializers

class ChatSessionSerializer(serializers.Serializer):
    customer_number = serializers.CharField()
    updated_at       = serializers.DateTimeField()