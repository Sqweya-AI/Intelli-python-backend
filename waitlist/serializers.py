from rest_framework import serializers

from .models import Waitlist

class WaitlistSerializer(serializers.ModelField):
    class Meta:
        model = Waitlist
        fields = '__all__'



