from rest_framework import serializers
from .models import Waitlist

# class WaitlistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Waitlist
#         fields = ['id', 'email_address', 'company_name', 'phone_number']



class WaitListSerializer(serializers.Serializer):
    email_address = serializers.CharField()
    company_name  = serializers.CharField()
    phone_number  = serializers.CharField()