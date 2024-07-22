from rest_framework import serializers

from .models import Waitlist

class WaitlistSerializer(serializers.ModelField):
    class Meta:
        model = Waitlist
        fields = ['id', 'email_address', 'company_name', 'phone_number']

    def save(self, validated_data):
        return Waitlist.objects.create(**validated_data)




