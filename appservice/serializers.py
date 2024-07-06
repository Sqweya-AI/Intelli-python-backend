from rest_framework import serializers

class ChatSessionSerializer(serializers.Serializer):
    customer_number = serializers.CharField()
    updated_at       = serializers.DateTimeField()



class MessageSerializer(serializers.Serializer):
    content     = serializers.CharField()
    answer      = serializers.CharField()
    created_at  = serializers.DateTimeField()
    sender      = serializers.CharField()
    chatsession = ChatSessionSerializer()
    
     