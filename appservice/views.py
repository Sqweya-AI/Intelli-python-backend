from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


from .models import AppService, ChatSession, Message

from business.models import Business


from .utils import get_answer_from_model

import os 
import logging
import requests 

# Define constants
INACTIVITY_TIMEOUT = 60*60  # 60 seconds for inactivity check
CHECK_INTERVAL     = 60*60  # 60 seconds interval for checking

# Load environment variables
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
VERSION         = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN")



def send_whatsapp_message(data):
    recipient = data.get("recipient")
    text = data.get("text")
    sending_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    
    response = requests.post(url, json=sending_data, headers=headers)

    if response.status_code != 200:
        print("WhatsApp failed to send message!")

    print('message is sent')
    # return response




def get_chat_history(chatsession):
    chat_history = []
    messages = Message.objects.filter(chatsession=chatsession).all()
    if messages:
        for message in messages:
            chat_history.append(
                {
                    "role" : "system",
                    "content" : message.answer
                },
                {
                    "role" : "user",
                    "content" : message.content
                }
            )
    

    return chat_history

# Define constants
INACTIVITY_TIMEOUT = 60*60  # 60 seconds for inactivity check
CHECK_INTERVAL = 60*60  # 60 seconds interval for checking

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")



@api_view(['POST'])
@permission_classes([AllowAny,])
@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        print(request.GET)

        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
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

        # business 
        id              = request.data.get('entry')[0]['id']
        customer_number = request.data.get('entry')[0]['changes'][0]['value']['contacts'][0]['wa_id']
        content         = request.data.get('entry')[0]['changes'][0]['value']['messages'][0]['text']['body']

        appservice = get_object_or_404(AppService, whatsapp_business_account_id=id)

        chatsession = ChatSession.objects.get_or_create(
            customer_number = customer_number,
            appservice = appservice,     
        )
        chat_history = get_chat_history(chatsession=chatsession)

        answer = get_answer_from_model(message=content, chat_history=chat_history)

        sendingData = {
            "recipient": customer_number,
            "text": answer
        }
        send_whatsapp_message(sendingData)

        message = Message.objects.create(
            content = content,
            answer  = answer,
            chatsession = chatsession
        )

        message.save()

        # print(request.data)
        return JsonResponse({'result': answer}, status=200)





"""
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "358127370715582",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15556221967",
              "phone_number_id": "381738275021314"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Sila"
                },
                "wa_id": "254751578687"
              }
            ],
            "messages": [
              {
                "from": "254751578687",
                "id": "wamid.HBgMMjU0NzUxNTc4Njg3FQIAEhgWM0VCMDg0NzYzMTExNDUyQURDNjRGRQA=",
                "timestamp": "1720051785",
                "text": {
                  "body": "y"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

"""
