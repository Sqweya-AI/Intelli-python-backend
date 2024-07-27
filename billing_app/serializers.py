from rest_framework import serializers
from .models import BillingModel


class BillingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingModel
        fields = '__all__'