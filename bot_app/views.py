# bot_app/views.py
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, api_view, action
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
import openai, os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from rest_framework import viewsets
from .models import ChatHistory
import requests, json
from .utils import *


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY', None)

# LLM_model = "gpt-3.5-turbo"
LLM_model = "gpt-4"
LLM_role_instructions ="\
    \
    Your name is Eli\
    You are hotel's customer service worker.\
    You are receiving enquiries from customers and handling them.\
    The name of the hotel you are working for is Hunters Royal Hotel.\
    Start by greeting the customer and asking how you can help them.\
    Use the data you are already aware of relating to the Hunters Royal Hotel, located in Ghana.\
    Your response should be in the same language the client has contacted the hotel in\
    (e.g if a customer speaks to you in swahili, reply in swahili, english for english .etc).\
    Keep your answers as short and concise as possible.\
    If a customer keeps asking useless questions, politely ask them to stop and focus on the purpose of the business, booking/reservation\
    If a customer asks for a reservation send them a link to the reservation page.\
    The link to the reservation page is: https://hunters-royal-hotel.herokuapp.com/reservation/, Be sure to tell them to click on the link\
    Refrain from telling the customer that they are speaking to a chatbot. or an AI agent\
    "

from django.core.cache import cache

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def chat(request):
    """
    Handle chat requests.
    Parameters:
    - user_input: The user's input for chat.
    Returns:
    - Response containing the chat request details and response.
    """
    user_input = request.data.get('user_input')
    user_id = request.user.id  # Get the user ID from the authenticated user

    # Get the existing chat history from the cache or initialize an empty list
    chat_history = cache.get(f'chat_history_{user_id}', [])

    try:
        chat_history.append({"role": "user", "content": user_input})
        response = openai.chat.completions.create(
        # response = openai.ChatCompletion.create(
            model=LLM_model,
            messages=[{"role": "system", "content": LLM_role_instructions}] + chat_history,
            max_tokens=256,
            temperature=0.5
        )
        assistant_response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": assistant_response})

        # Store the updated chat history in the cache
        cache.set(f'chat_history_{user_id}', chat_history, timeout=None)

        return Response({
            "request": "Enquiry Request",
            "input": user_input,
            "response": assistant_response
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

# translate view
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([]) 
def translate(request):
    """
    Handle translation requests.

    Parameters:
    - user_input: The user's input for translation.

    Returns:
    - Response containing the translation request details and response.
    """
    user_input = request.data.get('user_input')
    try:
        response = openai.chat.completions.create(
            model=LLM_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Translate the prompt you receive to swahili"},
                {"role": "user", "content": user_input},
            ],
            max_tokens=256,
            temperature=0.5
        )
        return Response({
            "request": "Translate Request",
            "input": user_input,
            "response": response.choices[0].message.content
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=500)

# User input's analysis
@authentication_classes([JWTAuthentication])
@permission_classes([]) 
class AnalyseView(APIView):
    def post(self, request):
        user_input = request.data.get('user_input')
        serializer = AnalysisSerializer(data={'user_input': user_input})
        if serializer.is_valid():
            try:
                response = openai.chat.completions.create(
                    model=LLM_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Analyse the prompt you receive and provide what conclusion you draw, as to what is the 1.Mood and 2.Feeling of the user who provided the input/query"
                        },
                        {
                            "role": "user",
                            "content": user_input
                        },
                    ],
                    max_tokens=256,
                    temperature=0.5
                )
                analysis_response = response.choices[0].message.content

                # Saving data to database
                serializer.save(user_input=user_input, analysis_response=analysis_response)

                return Response({
                    "request": "Analyse Request",
                    "input": user_input,
                    "response": analysis_response,
                    "analysis_id": serializer.instance.id  # Including the ID
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({
                    "error": f"Error during analysis: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class WhatsAppViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @csrf_exempt
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        data = request.data
        try:
            response = send_whatsapp_message(data)
            response.raise_for_status()  # Raise an exception for HTTP error responses
            return Response({"status": "success", "message": "Message sent successfully."})
        except requests.exceptions.HTTPError as http_err:
            return Response({"status": "failure", "message": f"HTTP error occurred: {http_err}"}, status=response.status_code)
        except requests.exceptions.RequestException as req_err:
            return Response({"status": "failure", "message": f"Error occurred: {req_err}"}, status=500)
        except Exception as err:
            return Response({"status": "failure", "message": f"An unexpected error occurred: {err}"}, status=500)
    
    @csrf_exempt
    @action(detail=False, methods=['post'])
    def chat_with_bot(self, request):
        input_text = request.data.get('input_text')
        response_text = bot_respond(input_text)
        return Response({"response": response_text})



# conversations
@api_view(['GET'])
def get_chat_histories(request):
    chat_histories = ChatHistory.objects.all()
    serializer = ChatHistorySerializer(chat_histories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def save_chat_history(request):
    serializer = ChatHistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        return verify_webhook_token(request)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            logging.info(f"Received webhook data: {data}")

            if 'object' in data and 'entry' in data:
                if data['object'] == 'whatsapp_business_account':
                    for entry in data['entry']:
                        changes = entry.get('changes', [])
                        for change in changes:
                            value = change.get('value', {})
                            metadata = value.get('metadata', {})
                            phoneNumber = metadata.get('display_phone_number')
                            phoneId = metadata.get('phone_number_id')
                            
                            contacts = value.get('contacts', [])
                            messages = value.get('messages', [])
                            statuses = value.get('statuses', [])

                            if contacts and messages:
                                if is_valid_message(messages[0]):
                                    profileName = contacts[0].get('profile', {}).get('name')
                                    whatsappId = contacts[0].get('wa_id')
                                    fromId = messages[0].get('from')
                                    messageId = messages[0].get('id')
                                    timestamp = messages[0].get('timestamp')
                                    textContent = messages[0].get('text', {}).get('body', '')

                                    logging.info(f'Message RECEIVED From {fromId}: {textContent}')

                                    bot_response = bot_respond(textContent, phoneNumber, whatsappId)

                                    sendingData = {
                                        "recipient": fromId,
                                        "text": bot_response
                                    }
                                    send_whatsapp_message(sendingData)
                                    
                                    logging.info(f'Reply SENT: {bot_response}')
                                    return JsonResponse({'success': True}, status=200)

                            if statuses:
                                for status in statuses:
                                    recipientId = status.get('recipient_id')
                                    messageId = status.get('id')
                                    messageStatus = status.get('status')
                                    timestamp = status.get('timestamp')
                                    logging.info(f'Status update: {messageStatus} for message {messageId}')
                                return JsonResponse({'status_received': True}, status=200)

            return JsonResponse({'invalid_data': True}, status=400)

        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'method_not_allowed': True}, status=405)

def clean_inactive_conversations(request):
    try:
        save_inactive_conversations(request)
        return JsonResponse({'success': True, 'message': 'Inactive conversations cleaned up.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
