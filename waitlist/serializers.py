from rest_framework import serializers
from .models import IntelliWaitList

class IntelliWaitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntelliWaitList
        fields = ['id', 'phone_number', 'company_name', 'email_address']

    
    
