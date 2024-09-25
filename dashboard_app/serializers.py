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

class DashboardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardModel
        fields = '__all__'

class HotelSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelSettingsModel
        fields = '__all__'
       

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettingsModel
        fields = '__all__'


