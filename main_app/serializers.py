# main_app/serializers.py
from rest_framework import serializers
from .models import *
from django.utils import dateparse
from dateutil import parser


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationModel
        fields = '__all__'

    def to_internal_value(self, data):
        """
        Parse check_in_date and check_out_date from the frontend format
        """
        data = dict(data)  # Make a mutable copy of the data dict

        # Parse check_in_date
        check_in_date_str = data.get('check_in_date')
        if check_in_date_str:
            data['check_in_date'] = parser.parse(check_in_date_str)

        # Parse check_out_date
        check_out_date_str = data.get('check_out_date')
        if check_out_date_str:
            data['check_out_date'] = parser.parse(check_out_date_str)

        return super().to_internal_value(data)

    def validate(self, data):
        """
        Check that check_in_date is before check_out_date.
        """
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        if check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date")

        return data