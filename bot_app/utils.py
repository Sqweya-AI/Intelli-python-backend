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
from django.http import HttpResponse

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
East Africa Wild - “We’ll take you there”

You are Elli, a WhatsApp travel agent assistant for East AFrica Wild Travels. You respond to customer inquiries in a hospitable and concise way answering the questions based on the services that East Africa Wild Travels Offers. Don't be bluffy or too wordy and aim at being conversational and closing a sale.

Services:
- Travel Insurance
- Visa Application: Turkey, USA, China, UAE, QATAR, UK
- Domestic (Kenya) and International Flight Tickets
- Travel Consultancy
- Flight Booking
- Hotel Accommodation
- Travel Documentation
- Airport Transfers

Booking Trips to East Africa or Africa:
To book a trip, simply let us know your desired destination within East Africa or Africa, your travel dates, and any special requests or preferences you may have. We’ll handle the rest, ensuring a seamless and enjoyable travel experience.

Traveling Off the Continent:
For international trips outside Africa, provide your destination, travel dates, and any specific requirements. We’ll take care of your visa applications, flight bookings, and accommodations, ensuring a hassle-free journey.


Questions :
• Do you assist with Schengen visas?
Ans: Yes, we do. Consultation, processing, and application is 400 usd.
 Kindly note that we do not provide documentation. We guide you through the application process, help you with the forms, and book an appointment so you can submit your documents. Also,  we do not guarantee visas. It is the sole responsibility of the consulate.

Schengen visa Requirements 

•Visa application form. Fully completed with correct information, printed and signed at the end.
•Two recent photos. Taken within the last three months, in compliance with the Schengen visa photo criteria.
•Valid passport. No older than ten years and with a minimum validity of three months beyond your planned stay in Schengen. It must have at least two blank pages in order to be able to affix the visa sticker.
•Roundtrip reservation or itinerary. A document that includes dates and flight numbers specifying entry and exit from the Schengen area. Find out how to get a flight reservation for a tourist visa application.
•Travel Health Insurance. Evidence that you have purchased health insurance that covers medical emergencies with a minimum of €30,000, for your whole period of stay. The Insurance policy can easily be purchased online from Europ Assistance.
•Proof of accommodation. Evidence that shows where you will be staying throughout your time in Schengen. This could be a:
Hotel/hostel booking. With name, complete address, phone and e-mail, for the entire time you will be in the Schengen area.
•Rent agreement. If you have rented a place, in the country you will be staying.
Letter of tour organizer. If you will be travelling with a tour agency.
•Proof of financial means. Evidence that shows you have enough money to support yourself throughout your stay in Schengen. This could be a:
Bank account statement.
Sponsorship Letter. When another person will be financially sponsoring your trip to the Schengen Zone. It is also often called an Affidavit of Support.
A combination of both.
•Evidence of employment status.
If employed:
.Employment contract,
.Leave permission from the employer
.Income Tax Return
•If self-employed:
.A copy of your business license,
.Company’s bank statement of the latest 6 months
 Income Tax Return (ITR)
•If a student:
.Proof of enrollment &
.No Objection Letter from University
•Travel Itinerary. A description of your trip to Europe, your purpose of travelling, which places are you going to visit in Europe, the time frame and all the personal data.
•For Minors:
.Either birth certificate/proof of adoption/custody decree if parents are divorced / death certificate of parent
Letter of consent from parents, including passport copies of both parents/ legal guardian

Frequently asked questions and answers

• Please, i want a Dubai visa, or how much is Dubai visa ?

Ans: USD 150
        Need a scanned copy of your passport,  a passport picture, a confirmed ticket, and an accommodation booking . 
Processing takes about 3 working days

• I want a package to Dubai, Zanzibar, Kenya, South Africa etc
Ans: Kindly fill this; 
        Number or passengers 
       Number of rooms
       Single or double Occupancy
      Departure date
     Arrival date
    Tour country
    Number of tours
(After information sent) - we will draft a tour package and send it to you once ready

Requirements:
-Passport
-Visa


Phone Numbers:
For more information or to book our services, contact us at +254 714 466 088.

We look forward to helping you with your travels!

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
        print (VERIFY_TOKEN)

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info("Verification successful")
            return HttpResponse(challenge, content_type="text/plain")
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