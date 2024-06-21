# chatbot/utils.py

import asyncio
import json
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
You are Elli, a WhatsApp assistant for Zora Furniture. You respond to customer inquiries in a hospitable and concise way answering the questions based on the services that Zora Furniture provides . Don't be bluffy and aim at being conversational and closing a sale by asking them to make a reservation by paying 50% of the amount by sending through MPESA to this Number:0794770061.
Living Room Furniture
Sofas:
Classic Leather Sofa
Description: High-quality leather sofa with a modern design.
Price: KES 135,000
Dimensions: 85" L x 35" W x 34" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA== 

Fabric Sofa Set
Description: Comfortable fabric sofa set including 3-seater, 2-seater, and 1-seater.
Price: KES 175,000
Dimensions: Varies by piece
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Coffee Tables:
Glass Top Coffee Table
Description: Elegant coffee table with a tempered glass top and metal frame.
Price: KES 40,000
Dimensions: 48" L x 24" W x 18" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Wooden Coffee Table
Description: Solid wood coffee table with storage space.
Price: KES 53,000
Dimensions: 42" L x 22" W x 18" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
TV Stands:
Modern TV Stand
Description: Sleek TV stand with ample storage and cable management.
Price: KES 66,000
Dimensions: 60" L x 16" W x 24" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Rustic TV Stand
Description: TV stand with a rustic finish and multiple compartments.
Price: KES 60,000
Dimensions: 55" L x 18" W x 24" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Bedroom Furniture
Beds:
Queen Size Bed Frame
Description: Sturdy queen size bed frame with upholstered headboard.
Price: KES 93,000
Dimensions: 85" L x 65" W x 50" H
Image: Queen Size Bed Frame Image
King Size Bed Frame
Description: Spacious king size bed frame with wooden finish.
Price: KES 119,000
Dimensions: 89" L x 81" W x 50" H
Image:https://www.instagram.com/reel/C7w7d0agw5s/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Dressers:
6-Drawer Dresser
Description: Modern dresser with six spacious drawers.
Price: KES 66,000
Dimensions: 60" L x 18" W x 36" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA== 

Antique Dresser
Description: Vintage-style dresser with intricate detailing.
Price: KES 80,000
Dimensions: 55" L x 20" W x 34" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Nightstands:
Modern Nightstand
Description: Compact nightstand with two drawers.
Price: KES 26,000
Dimensions: 20" L x 16" W x 24" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Classic Nightstand
Description: Wooden nightstand with a single drawer and open shelf.
Price: KES 23,000
Dimensions: 18" L x 15" W x 25" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Dining Room Furniture
Dining Tables:
Extendable Dining Table
Description: Versatile dining table with an extendable feature.
Price: KES 106,000
Dimensions: 60" - 80" L x 40" W x 30" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Round Dining Table
Description: Elegant round dining table with a pedestal base.
Price: KES 79,000
Dimensions: 48" Diameter x 30" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Dining Chairs:
Upholstered Dining Chair
Description: Comfortable dining chair with fabric upholstery.
Price: KES 20,000 each
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Wooden Dining Chair
Description: Classic wooden dining chair with a cushioned seat.
Price: KES 17,000 each
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Sideboards:
Modern Sideboard
Description: Stylish sideboard with ample storage space.
Price: KES 93,000
Dimensions: 70" L x 18" W x 36" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
Vintage Sideboard
Description: Antique-style sideboard with intricate carvings.
Price: KES 100,000
Dimensions: 65" L x 20" W x 34" H
Image:https://www.instagram.com/p/C7RW33nIEgR/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
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
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return JsonResponse({'challenge': challenge})
        else:
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