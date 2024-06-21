# chatbot/utils.py

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
import os
import openai
import requests
from django.core.cache import cache
from django.http import JsonResponse
from .models import ChatHistory

# Define constants
INACTIVITY_TIMEOUT = 60*60  # 60 seconds for inactivity check
CHECK_INTERVAL = 60*60  # 60 seconds interval for checking

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Instantiate OpenAI client
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

# Get the current time and date
the_time = datetime.now().strftime('%H:%M')
the_date = datetime.now().strftime('%Y-%m-%d')

LLM_model = "gpt-4" 
LLM_role_instructions = f"""
Briden Travels - “We’ll take you there”

You are Elli, a WhatsApp travel agent assistant for Brriden Travels. You respond to customer inquiries in a hospitable and concise way answering the questions based on the services that Briden Travel Offers. Don't be bluffy and aim at being conversational and closing a sale.

Services:
-Travel Insurance
-Visa Application - Turkey, USA, China, UAE, QATAR, UK
-Domestic (Kenya) and International Flight Tickets
-Jobs  to UAE, QATAR
-Travel Consultancy
-Flight booking
-Hotel Accomodation
-Travel Documentation
-Airport Transfers

Jobs  Abroad

-House Maid Qatar - 20% commission, Salary 200Qr

Procedure :
Submit CV, attaching your passport in PDF
Send to info@bridenjobs.co.ke
 
-Security Guards Qatar- 20% commission Salary 2500Qr

Procedure :
Submit CV, attaching your passport in PDF
Send to info@bridenjobs.co.ke
 
-Male and Female  Qatar Drivers - 20% commission Salary 3500Qr. 

Procedure :

Submit CV, attaching your passport in PDF and Drivers license.
Send to info@bridenjobs.co.ke
 (Quick Hiring, Interview is Physical you will practically drive to prove you are fit for the job.) See you then!!! 

Riders in Dubai - Salary 2000 AED

Requirements:
-Passport
-Certificate of good conduct
-Medical Report
-Age 21 -35
-Motorcycle license


Phone number: +254 714 466 088

"""

print(the_time)

active_conversations = {}

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
    return response

def verify_webhook_token(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        logging.info(f"Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
        logging.info(f"Stored VERIFY_TOKEN: {VERIFY_TOKEN}")

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info("Verification successful")
            response = JsonResponse({'hub.challenge': challenge})
            response["Access-Control-Allow-Origin"] = "*"
            return response
        else:
            logging.warning("Verification failed")
            return JsonResponse({'error': 'Verification token mismatch'}, status=403)
    
    return JsonResponse({'method_not_allowed': True}, status=405)

def bot_respond(input_text, sender_id, recipient_id):
    try:
        response_text = bot_process(input_text, sender_id, recipient_id)
        return response_text
    except Exception as e:
        error_message = f"Error generating bot response: {e}"
        print(error_message)
        return f"Sorry, I couldn't generate a response at the moment. Error: {error_message}"

def is_valid_message(message):
    text_content = message.get('text', {}).get('body', '').lower()
    from_id = message.get('from')

    if len(text_content.split()) < 1:
        print(f'{len(text_content.split())} words long message')
        return False

    if from_id in active_conversations:
        last_activity = active_conversations[from_id]
        if datetime.now() - last_activity < timedelta(seconds=INACTIVITY_TIMEOUT):
            active_conversations[from_id] = datetime.now()
        else:
            del active_conversations[from_id]
            print('Inactive conversation')
            return False
    else:
        active_conversations[from_id] = datetime.now()
    return True

def save_inactive_conversations(request):
    current_time = time.time()
    saved_conversations = []  # List to store the phone numbers of saved conversations

    for from_id, last_activity_time in list(active_conversations.items()):
        sender_id = from_id
        recipient_id = from_id  # Assuming recipient_id is the same as from_id

        # Save chat history without checking inactivity timeout
        chat_history = cache.get(f'chat_history_{sender_id}_{recipient_id}', [])

        save_chat_history(sender_id, recipient_id, chat_history)

        # Add the phone number to the list of saved conversations
        saved_conversations.append(recipient_id)

        cache.delete(f'chat_history_{sender_id}_{recipient_id}')
        cache.delete(f'last_activity_{sender_id}_{recipient_id}')
        cache.delete(f'inactivity_message_sent_{sender_id}_{recipient_id}')

        del active_conversations[from_id]

    # Check if any conversations were saved
    if saved_conversations:
        # Construct the message with the phone numbers of saved conversations
        whatsapp_message = f'Convo auto saved: {", ".join(saved_conversations)}'
        sendingData = {
            "recipient": '255755888555',
            "text": whatsapp_message
        }
        print('=================================')
        print(whatsapp_message)
        print('=================================')
        send_whatsapp_message(sendingData)
    else:
        # If no conversations were saved, send a message indicating no activity
        sendingData = {
            "recipient": '255755888555',
            "text": 'No activity, no numbers were found in saved conversations'
        }
        print('=================================')
        print('No activity')
        print('=================================')
        send_whatsapp_message(sendingData)

# Schedule the next check
    # request.loop.call_later(CHECK_INTERVAL, save_inactive_conversations, request)


def bot_process(input_text, sender_id, recipient_id):
    user_input = input_text
    chat_history = cache.get(f'chat_history_{sender_id}_{recipient_id}', [])

    inactivity_message = (
        "You were inactive for a minute there.\n"
        "If you would like to continue with our last issue reply with '*YES*'.\n"
        "If you would like me to assist you with a new issue now, please reply with '*NEW*' or '*NEW ISSUE*'."
    )

    try:
        # Remove inactivity checks
        # last_activity = cache.get(f'last_activity_{sender_id}_{recipient_id}', time.time())
        # inactivity_message_sent = cache.get(f'inactivity_message_sent_{sender_id}_{recipient_id}', False)
        
        # Append user input to chat history
        chat_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=LLM_model,
            messages=[{"role": "system", "content": LLM_role_instructions}] + chat_history,
            max_tokens=256,
            temperature=0.5
        )

        assistant_response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": assistant_response})

        # Save chat history after every interaction
        cache.set(f'chat_history_{sender_id}_{recipient_id}', chat_history, timeout=None)
        save_chat_history(sender_id, recipient_id, chat_history)

        return assistant_response

    except Exception as e:
        return f"Error generating bot response: {e}"



def continue_conversation(sender_id, recipient_id, chat_history):
    cache.set(f'chat_history_{sender_id}_{recipient_id}', chat_history, timeout=None)
    return "Great! Let's continue our conversation."

from django.db.models import F

def save_chat_history(sender_id, recipient_id, chat_history):
    chat_record, created = ChatHistory.objects.update_or_create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        defaults={'chat_history': chat_history}
    )
    
    if created:
        message = f'New chat history created for: {recipient_id}'
    else:
        message = f'Chat history updated for: {recipient_id}'
    
    sendingData = {
        "recipient": '255755888555',
        "text": message
    }
    # send_whatsapp_message(sendingData)
    print(f'\n {message}')