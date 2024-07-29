from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import ChatSessionSerializer, MessageSerializer, AppServiceSerializer
from .models import AppService, ChatSession, Message
from .utils  import bot_process
from .utils  import send_whatsapp_message
from .utils  import check_for_escalated_events

from business.models import Business
from notifications.models import Notification

import os 
import logging
from typing import Dict, Any


# Load environment variables
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
VERSION         = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN")
ASSISTANT_ID    = os.getenv("ASSISTANT_ID")


logger = logging.getLogger(__name__)

def get_chat_history(chatsession):
    chat_history = []
    messages = Message.objects.filter(chatsession=chatsession).order_by('-created_at')[:3]
    logger.info(messages)
    if messages:
        for message in messages:
            chat_history.append({"role" : "system", "content" : message.answer if message.answer else ' ' })
            chat_history.append({"role" : "user",   "content" : message.content if message.content else ' '})
    

    return chat_history


def handle_verification(request) -> HttpResponse:
    mode      = request.GET.get('hub.mode')
    token     = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')

    logger.info(f"Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
    logger.info(f"Stored VERIFY_TOKEN: {VERIFY_TOKEN}")

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("Verification successful")
        return HttpResponse(challenge, content_type="text/plain")
    else:
        logger.warning("Verification failed")
        return JsonResponse({'error': 'Verification token mismatch'}, status=status.HTTP_403_FORBIDDEN)


def extract_whatsapp_data(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        entry   = data['entry'][0]
        changes = entry['changes'][0]['value']
        if 'messages' in changes:
            return {
                'id': entry['id'],
                'customer_number': changes['contacts'][0]['wa_id'],
                'customer_name'  : changes['contacts'][0]['profile']['name'],
                'content'        : changes['messages'][0]['text']['body']
            }
        else:
            return {}
    except KeyError:
        status = changes['statuses'][0]['status']
        logger.info(f"Received status: {status}")
        return {'status': status}


def handle_whatsapp_message(data: Dict[str, Any]) -> JsonResponse:   
    if data == {}:
        return Response(status=200) 
    appservice = get_object_or_404(AppService, whatsapp_business_account_id=data['id'])
    chatsession, created = ChatSession.objects.get_or_create(
        customer_number=data['customer_number'],
        appservice=appservice,
    )

    if created:
        chatsession.customer_name = data['customer_name']
        chatsession.save()

    if not chatsession.is_handle_by_human and data['content']:
        answer = bot_process(
            input_text=data['content'],
            appservice=appservice,
            recipient_id=data['customer_number'],
            assistant_id=appservice.assistant_id
        )
    else:
        answer = 'Please wait for our response..'

    send_whatsapp_message({
        "recipient": data['customer_number'],
        "text": answer,
        "phone_number_id": appservice.phone_number_id,
        "access_token": appservice.access_token
    })

    Message.objects.create(
        content=data['content'],
        answer=answer,
        chatsession=chatsession,
        sender='ai'
    )

    # check for escalated events 
    events = check_for_escalated_events(data['content'])
    logger.info(events)
    if 'user_request_no_alert' not in events['escalated_events']:
        notif = events 
        notif['chatsession'] = chatsession
        notif['channel']     = 'whatsapp'
        notification = Notification.objects.create(**notif)
        notification.save()
    return JsonResponse({'result': answer}, status=status.HTTP_201_CREATED)


def handle_other_message(data: Dict[str, Any]) -> JsonResponse:
    appservice = get_object_or_404(AppService, phone_number=data['phone_number'])
    chatsession, _ = ChatSession.objects.get_or_create(
        customer_number=data['customer_number'],
        appservice=appservice,
    )

    send_whatsapp_message({
        "recipient": data['customer_number'],
        "text": data['answer'],
        "phone_number_id": appservice.phone_number_id,
        "access_token": appservice.access_token
    })

    Message.objects.create(
        content=data['content'],
        answer=data['answer'],
        chatsession=chatsession,
        sender='human'
    )

    return JsonResponse({'result': data['answer']}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def webhook(request):
    if request.method == 'GET':
        return handle_verification(request)
    
    elif request.method == 'POST':
        data = request.data
        
        if 'object' in data and 'entry' in data:
            whatsapp_data = extract_whatsapp_data(data)
            if 'status' not in whatsapp_data and whatsapp_data != {}:
                return handle_whatsapp_message(whatsapp_data)
            else:
                return Response(status=200)
            
        else:
            return handle_other_message(data)
        

                

@api_view(['POST'])
@permission_classes([AllowAny,])
@csrf_exempt
def takeover(request):
    # {
    #     "phone_number" : "",
    #     "customer_number" : ""
    # }
    if request.method == 'POST': 
        phone_number          = request.data.get('phone_number', None)
        phone_number          = phone_number.strip()
        customer_number       = request.data.get('customer_number', None)
        appservice            = get_object_or_404(AppService, phone_number=phone_number)

        chatsession  = ChatSession.objects.filter(
            customer_number = customer_number,
            appservice = appservice
        ).first()
      
        chatsession.is_handle_by_human = True 
        chatsession.save()

        return Response(
            {
                'message' : 'You took over the AI Assistant'
            },
            status=200
        )



@api_view(['POST'])
@permission_classes([AllowAny,])
@csrf_exempt
def handover(request):
    if request.method == 'POST': 
        phone_number          = request.data.get('phone_number', None)
        customer_number       = request.data.get('customer_number', None)
        appservice            = get_object_or_404(AppService, phone_number=phone_number)

        chatsession, created  = ChatSession.objects.get_or_create(
            customer_number = customer_number,
            appservice = appservice
        )

        chatsession.is_handle_by_human = False 
        chatsession.save()

        return Response(
            {
                'message' : 'You hand over the AI Assistant'
            },
            status=200
        )



@api_view(['GET'])
@permission_classes([AllowAny,])
@csrf_exempt
def chatsessions_history(request, phone_number):
    appservice   = get_object_or_404(AppService, phone_number=phone_number)
    if appservice:
        chatsession  = ChatSession.objects.filter(appservice=appservice).prefetch_related('messages')
        serializer   = ChatSessionSerializer(chatsession, many=True)

        return Response(serializer.data, status=200)
    



@api_view(['GET'])
@permission_classes([AllowAny,])
@csrf_exempt
def messages_history(request, phone_number, customer_number):
    appservice   = get_object_or_404(AppService, phone_number=phone_number)
    if appservice:
        chatsession  = ChatSession.objects.filter(appservice=appservice, customer_number=customer_number).first()
        messages     = Message.objects.filter(chatsession=chatsession)
        serializer   = MessageSerializer(messages, many=True)

        return Response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny,])
@csrf_exempt
def appservices_list(request, owner):
    owner = owner.strip()
    business = get_object_or_404(Business, owner=owner)
    if business:
        appservices = AppService.objects.filter(business=business)
        serializer  = AppServiceSerializer(appservices, many=True)
        return Response(serializer.data, status=200)
    

