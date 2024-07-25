from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import ChatSessionSerializer, MessageSerializer, AppServiceSerializer
from .models import AppService, ChatSession, Message
from business.models import Business
from .utils import get_answer_from_model, bot_process

import os 
import json 
import logging
import requests 



# Load environment variables
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
VERSION         = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN")
ASSISTANT_ID    = os.getenv("ASSISTANT_ID")



def send_whatsapp_message(data):
    recipient = data.get("recipient")
    text = data.get("text")
    phone_number_id = data.get('phone_number_id')
    access_token    = data.get('access_token')

    print('Le text a envoyé: ',text)
    sending_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{phone_number_id}/messages"

    try:
      response = requests.post(url, json=sending_data, headers=headers)
    except Exception as e:
        print('Sending Error :', e)

    if response.status_code != 200:
        print(response.status_code)
        print(response.json())
        print("WhatsApp failed to send message!")
        print()

    # return response




def get_chat_history(chatsession):
    chat_history = []
    messages = Message.objects.filter(chatsession=chatsession).order_by('-created_at')[:3]
    print(messages)
    if messages:
        for message in messages:
            chat_history.append({"role" : "system", "content" : message.answer if message.answer else ' ' })
            chat_history.append({"role" : "user",   "content" : message.content if message.content else ' '})
    

    return chat_history




@api_view(['GET','POST'])
@permission_classes([AllowAny,])
@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        mode      = request.GET.get('hub.mode')
        token     = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        print(mode, token, challenge)
        
        logging.info(f"Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
        logging.info(f"Stored VERIFY_TOKEN: {VERIFY_TOKEN}")
        print (VERIFY_TOKEN)

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info("Verification successful")
            return HttpResponse(challenge, content_type="text/plain")
 
        else:
            logging.warning("Verification failed")
            return JsonResponse({'error': 'Verification token mismatch'}, status=403)
    
    elif request.method == 'POST':
        print(request.data)
        # this is from whatsapp
        if 'object' in request.data and 'entry' in request.data:
            try:
                id              = request.data.get('entry')[0]['id']
                print('id: ',id)
                customer_number = request.data.get('entry')[0]['changes'][0]['value']['contacts'][0]['wa_id']
                print('customer_number', customer_number)
                customer_name   = request.data.get('entry')[0]['changes'][0]['value']['contacts'][0]['profile']['name']
                print("customer_name", customer_name)
                content         = request.data.get('entry')[0]['changes'][0]['value']['messages'][0]['text']['body']
                print("content", content)
            except Exception as e:
                status          = request.data.get('entry')[0]['changes'][0]['value']['statuses'][0]['status']
                print("status", status)
                return Response({
                    'result' : "Status Well Received"
                }, status=200)

            appservice = get_object_or_404(AppService, whatsapp_business_account_id=id)
            assistant_id = appservice.assistant_id
            print('phone_number',appservice.phone_number)
            print('phone_number_id',appservice.phone_number_id)
            chatsession, created = ChatSession.objects.get_or_create(
                customer_number = customer_number,
                appservice      = appservice,     
            )

            chatsession.customer_name = customer_name
            chatsession.save()

            chat_history = get_chat_history(chatsession=chatsession)
            answer = 'Wait for my response..'

            # ai or human logic
            if chatsession.is_handle_by_human == False and content is not None:
                # answer = get_answer_from_model(message=content, chat_history=chat_history)
                answer = bot_process(input_text=content, appservice=appservice, recipient_id=customer_number, assistant_id=assistant_id)
                print('answer from model: ',answer)


            sendingData = {
                "recipient"       : customer_number,
                "text"            : answer,
                "phone_number_id" : appservice.phone_number_id,
                "access_token"    : appservice.access_token
            }
            send_whatsapp_message(sendingData)
            message = Message.objects.create(
                content     = content,
                answer      = answer,
                chatsession = chatsession,
                sender      = 'ai'
            )

            message.save()

            # print(request.data)
            return JsonResponse({'result': answer}, status=201)

        else:
            try:
                customer_number = request.data.get('customer_number', None)
                customer_name   = request.data.get('customer_name', None)
                phone_number    = request.data.get('phone_number', None)
                content         = request.data.get('content', None)
                answer          = request.data.get('answer', None)


            except Exception as e:
                print(e)
            
            appservice = get_object_or_404(AppService, phone_number=phone_number)
            chatsession, created = ChatSession.objects.get_or_create(
                customer_number = customer_number,
                appservice = appservice,     
            )

            chatsession.customer_name = customer_name
            chatsession.save()
            chat_history = get_chat_history(chatsession=chatsession)

            sendingData = {
                "recipient"       : customer_number,
                "text"            : answer,
                "phone_number_id" : appservice.phone_number_id,
                "access_token"    : appservice.access_token
            }
            send_whatsapp_message(sendingData)
            message = Message.objects.create(
                content     = content,
                answer      = answer,
                chatsession = chatsession,
                sender      = 'human'
            )

            message.save()

            # print(request.data)
            return JsonResponse({'result': answer}, status=201)

                

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
    

