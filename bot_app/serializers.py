# bot_app/serializers.py
from rest_framework import serializers
from .models import *

class ChatHistorySerializer(serializers.ModelSerializer):
  """
  Serializer for the ChatHistory model, including all fields.
  """
  class Meta:
    model = ChatHistory
    fields = '__all__'  


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__' 
