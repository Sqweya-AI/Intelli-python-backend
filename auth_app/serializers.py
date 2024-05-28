# auth_app/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'password','is_email_verified', 'company_name', 'username']
        extra_kwargs = {
            'password': {'write_only': True}
        }