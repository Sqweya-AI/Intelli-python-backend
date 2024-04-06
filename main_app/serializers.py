# main_app/serializers.py
from rest_framework import serializers
from .models import *

class ReservationSerializer(serializers.ModelSerializer):
    check_in_date = serializers.DateTimeField(input_formats=['%m/%d/%Y'])
    check_out_date = serializers.DateTimeField(input_formats=['%m/%d/%Y'])

    class Meta:
        model = ReservationModel
        fields = '__all__'

    def validate(self, data):
        """
        Check that check_in_date is before check_out_date.
        """
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        return data



class WaitlistMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistMember
        fields = '__all__'