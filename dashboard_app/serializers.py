from rest_framework import serializers
from .models import * 

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__' 
    
class AgentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRole
        fields = '__all__'

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactChannel
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class DashboardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardModel
        fields = '__all__'