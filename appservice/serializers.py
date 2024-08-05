from rest_framework import serializers
from business.serializers import BusinessSerializer

from notifications.serializers import NotificationSerializer

class MessageSerializer(serializers.Serializer):
    id          = serializers.IntegerField()
    content     = serializers.CharField()
    answer      = serializers.CharField()
    created_at  = serializers.DateTimeField()
    sender      = serializers.CharField()
    # chatsession = ChatSessionSerializer()


class MessageAnalysisSerializer(serializers.Serializer):
    id         = serializers.IntegerField()
    content    = serializers.CharField()


class ChatSessionSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    customer_number = serializers.CharField()
    messages        = MessageSerializer(many=True, read_only=True)
    updated_at      = serializers.DateTimeField()


class ChatSessionNotificationSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    customer_number = serializers.CharField()
    customer_name   = serializers.CharField()
    notifications   = NotificationSerializer(many=True, read_only=True)
    updated_at      = serializers.DateTimeField()


class ChatSessionListSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    customer_number = serializers.CharField()
    updated_at      = serializers.DateTimeField()


class AppServiceSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    business        = BusinessSerializer()
    phone_number_id = serializers.CharField()
    phone_number    = serializers.CharField()
    app_secret      = serializers.CharField()
    created_at      = serializers.DateTimeField()
    chatsessions    = ChatSessionListSerializer(many=True, read_only=True)
    whatsapp_business_account_id = serializers.CharField()


class AppServiceListSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    phone_number    = serializers.CharField()
    created_at      = serializers.DateTimeField()
    
    

