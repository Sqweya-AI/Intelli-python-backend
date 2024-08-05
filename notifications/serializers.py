from rest_framework import serializers
# from appservice.serializers import ChatSessionListSerializer


class NotificationSerializer(serializers.Serializer):
    id               = serializers.IntegerField()
    # chatsession      = ChatSessionListSerializer()
    text             = serializers.CharField()
    escalated_events = serializers.JSONField()
    channel          = serializers.CharField()
    connection_id    = serializers.CharField()
    created_at       = serializers.DateTimeField()


