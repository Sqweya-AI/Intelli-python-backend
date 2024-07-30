from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


from .models import SentimentAnalysis
from .utils import sentiment_analyzer
from .serializers import SentimentAnalysisSerializer

from appservice.models import AppService
from appservice.models import ChatSession
from appservice.models import Message
from appservice.serializers import MessageAnalysisSerializer


import logging
import json 

logger = logging.getLogger(__name__)

def get_chat_history_for_analysis(chatsession):
    messages = Message.objects.filter(chatsession=chatsession).order_by('-created_at')[:10]
    # logger.info(messages)
    serializer = MessageAnalysisSerializer(messages, many=True)

    return serializer.data


@api_view(['POST'])
@permission_classes([AllowAny])
def sentiment_analysis(request):
    customer_number = request.data.get('customer_number')
    phone_number    = request.data.get('phone_number')
    print(phone_number)
    appservice      = get_object_or_404(AppService, phone_number=phone_number)
    chatsession     = ChatSession.objects.filter(appservice=appservice, customer_number=customer_number).first()
    print(chatsession)
    message_list    = get_chat_history_for_analysis(chatsession=chatsession)
    analysis        = sentiment_analyzer(message_list=json.dumps(message_list))

    data = {}
    data['chatsession'] = chatsession
    data['sentiments']  = analysis

    sentiment = SentimentAnalysis.objects.create(**data)
    sentiment.save()

    serializer = SentimentAnalysisSerializer(sentiment)

    return Response(serializer.data, status=status.HTTP_200_OK)



"""
{
    "phone_number" : "233536620120",
    "customer_number" : "233536633465"
}
"""