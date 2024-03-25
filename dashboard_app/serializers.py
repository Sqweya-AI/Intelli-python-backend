# dashboard_app/serializers.py
from rest_framework import serializers
from .models import * 

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentModel
        fields = '__all__' 
    
class AgentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRoleModel
        fields = '__all__'

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactChannelModel
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationModel
        fields = '__all__'

class DashboardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardModel
        fields = '__all__'

class HotelSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelSettingsModel
        fields = [
            'hotel_name',
            'min_advance_booking',
            'max_advance_booking',
            'hotel_capacity',
            'check_in_time',
            'check_out_time',
            'hotel_address',
            'hotel_phone',
            'hotel_email',
            'cancellation_policy',
            'default_currency',
            'room_types',
            'accepted_payment_methods',
            'hotel_amenities'
        ]

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettingsModel
        fields = [
            'name',
            'user',
            'email',
            'phone',
            'notification_settings',
            'user_preferences'
        ]


