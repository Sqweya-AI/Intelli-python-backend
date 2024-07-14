from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from .utils import get_flight_offers, get_airport_code, extract_travel_details
from .serializers import ChatSessionSerializer, MessageSerializer
from .models import AppService, ChatSession, Message
from business.models import Business
import openai
import os 
import json 
import logging
import requests 
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)



# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

ASSISTANT_ID = os.getenv("ASSISTANT_ID")


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

    try:
      response = requests.post(url, json=sending_data, headers=headers)
    except Exception as e:
        print('Sending Error :', e)

    if response.status_code != 200:
        print(response.status_code)
        print("WhatsApp failed to send message!")
        print()

    # return response




def get_chat_history(chatsession):
    chat_history = []
    messages = Message.objects.filter(chatsession=chatsession)
    if messages:
        for message in messages:
            chat_history.append({"role": "assistant", "content": message.answer if message.answer else ' '})
            chat_history.append({"role": "user", "content": message.content if message.content else ' '})
    return chat_history
  
@api_view(['GET','POST'])
@permission_classes([AllowAny,])
@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        else:
            return JsonResponse({'error': 'Verification token mismatch'}, status=403)
    
    elif request.method == 'POST':
        try:
            data = request.data
            logger.info(f"Received POST data: {data}")

            if 'object' in data and data['object'] == 'whatsapp_business_account':
                for entry in data['entry']:
                    changes = entry['changes']
                    for change in changes:
                        value = change['value']
                        if 'messages' in value:
                            for message in value['messages']:
                                if message['type'] == 'text':
                                    customer_number = message['from']
                                    content = message['text']['body']
                                    customer_name = value['contacts'][0]['profile']['name']
                                    
                                    # Process the message
                                    appservice = AppService.objects.get(whatsapp_business_account_id=entry['id'])
                                    chatsession, _ = ChatSession.objects.get_or_create(
                                        customer_number=customer_number,
                                        appservice=appservice
                                    )
                                    chatsession.customer_name = customer_name
                                    chatsession.save()

                                    if not chatsession.is_handle_by_human:
                                        response = process_message(content)

                                        # Send response back to WhatsApp
                                        sendingData = {
                                            "recipient": customer_number,
                                            "text": response
                                        }
                                        send_whatsapp_message(sendingData)

                                        # Save the message to the database
                                        Message.objects.create(
                                            content=content,
                                            answer=response,
                                            chatsession=chatsession,
                                            sender='ai'
                                        )

                                    return JsonResponse({'status': 'Message processed'}, status=200)

            return JsonResponse({'status': 'No messages to process'}, status=200)

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def process_message(content):
    travel_details = extract_travel_details(content)
    flight_info = get_flight_info(travel_details)
    return generate_ai_response(content, flight_info)

def get_flight_info(travel_details):
    if travel_details and all(travel_details.values()):
        flight_offers = get_flight_offers(travel_details['origin'], travel_details['destination'], travel_details['date'])
        if flight_offers and 'data' in flight_offers:
            flight_info = "Real-time flight offers:\n"
            for offer in flight_offers['data']:
                price = offer['price']['total']
                currency = offer['price']['currency']
                airline_code = offer['validatingAirlineCodes'][0]
                airline = flight_offers['dictionaries']['carriers'].get(airline_code, airline_code)
                
                departure = datetime.fromisoformat(offer['itineraries'][0]['segments'][0]['departure']['at'])
                arrival = datetime.fromisoformat(offer['itineraries'][0]['segments'][-1]['arrival']['at'])
                
                duration = arrival - departure
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                flight_info += (f"- {airline}: {price} {currency}\n"
                                f"  Departure: {departure.strftime('%Y-%m-%d %H:%M')}\n"
                                f"  Arrival: {arrival.strftime('%Y-%m-%d %H:%M')}\n"
                                f"  Duration: {hours}h {minutes}m\n"
                                f"  Stops: {len(offer['itineraries'][0]['segments']) - 1}\n\n")
        else:
            flight_info = "No flight offers found for the specified route and date."
    else:
        missing_info = [key for key, value in travel_details.items() if not value]
        flight_info = f"Unable to search for flights. Missing information: {', '.join(missing_info)}."
    
    return flight_info

def generate_ai_response(content, flight_info):
    thread = openai.beta.threads.create()
    
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"{content}\n\nFlight Information:\n{flight_info}"
    )
    
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    
    while run.status != 'completed':
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value





                

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
        customer_number       = request.data.get('customer_number', None)
        appservice            = get_object_or_404(AppService, phone_number=phone_number)

        chatsession, existed  = ChatSession.objects.get_or_create(
            customer_number = customer_number,
            appservice = appservice
        )

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

        chatsession, existed  = ChatSession.objects.get_or_create(
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
        chatsession  = ChatSession.objects.filter(appservice=appservice)
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



"""

1. takeover endpoint 
customer_number phone number of the customer 
phone_number is the business phone number  


2. takeover message endpoint 
customer_number phone number of the customer 
phone_number is the business phone number  
content is the customer message 
answer is the message of the business 


3. chatsession history 
phone_number is the business phone number  


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

# Meta webhook Request Objects 
"""
1. 
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
                "id": "wamid.HBgMMjU0NzUxNTc4Njg3FQIAEhggMzk4NTk4QjNCQzMxM0Y0NEQ2RjdDMDNDMzE5RDg2OUQA",
                "timestamp": "1720179745",
                "text": {
                  "body": "Hello"
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



2. 
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
            "statuses": [
              {
                "id": "wamid.HBgMMjU0NzUxNTc4Njg3FQIAERgSNURGQjM3QTg1NEUxQUVFMEU0AA==",
                "status": "sent",
                "timestamp": "1720179748",
                "recipient_id": "254751578687",
                "conversation": {
                  "id": "0f007f9a9b0874573fb36e961ef0e8bc",
                  "expiration_timestamp": "1720265640",
                  "origin": {
                    "type": "service"
                  }
                },
                "pricing": {
                  "billable": true,
                  "pricing_model": "CBP",
                  "category": "service"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

3. 

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
            "statuses": [
              {
                "id": "wamid.HBgMMjU0NzUxNTc4Njg3FQIAERgSNURGQjM3QTg1NEUxQUVFMEU0AA==",
                "status": "read",
                "timestamp": "1720179749",
                "recipient_id": "254751578687",
                "conversation": {
                  "id": "0f007f9a9b0874573fb36e961ef0e8bc",
                  "origin": {
                    "type": "service"
                  }
                },
                "pricing": {
                  "billable": true,
                  "pricing_model": "CBP",
                  "category": "service"
                }
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
