from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    content     = serializers.CharField()
    answer      = serializers.CharField()
    created_at  = serializers.DateTimeField()
    sender      = serializers.CharField()
    # chatsession = ChatSessionSerializer()


class ChatSessionSerializer(serializers.Serializer):
    customer_number = serializers.CharField()
    messages        = MessageSerializer(many=True, read_only=True)
    updated_at      = serializers.DateTimeField()




    
     