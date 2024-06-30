import os
import time
from datetime import datetime
import requests
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from openai import OpenAI
from .models import ChatHistory

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Replace this with your actual Assistant ID
ASSISTANT_ID = 'YOUR_ASSISTANT_ID'

# Instantiate OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

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
            return HttpResponse(challenge, content_type="text/plain")
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

def bot_process(input_text, sender_id, recipient_id):
    thread_id = cache.get(f'thread_{sender_id}_{recipient_id}')

    try:
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            cache.set(f'thread_{sender_id}_{recipient_id}', thread_id, timeout=None)

        # Add the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=input_text
        )

        # Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the run to complete
        while run.status not in ["completed", "failed", "expired"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status != "completed":
            return f"Sorry, there was an issue processing your request. Status: {run.status}"

        # Retrieve the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_response = messages.data[0].content[0].text.value

        # Save chat history
        save_chat_history(sender_id, recipient_id, [
            {"role": "user", "content": input_text},
            {"role": "assistant", "content": assistant_response}
        ])

        return assistant_response

    except Exception as e:
        return f"Error generating bot response: {e}"

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
    
    print(f'\n {message}')

def save_inactive_conversations(request):
    saved_conversations = []

    for from_id in list(cache.keys('thread_*')):
        sender_id, recipient_id = from_id.split('_')[1:]
        thread_id = cache.get(from_id)

        if thread_id:
            # Retrieve the last few messages from the thread
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=5)
            chat_history = [
                {"role": msg.role, "content": msg.content[0].text.value}
                for msg in reversed(messages.data)
            ]

            save_chat_history(sender_id, recipient_id, chat_history)
            saved_conversations.append(recipient_id)

            cache.delete(from_id)

    if saved_conversations:
        whatsapp_message = f'Convo auto saved: {", ".join(saved_conversations)}'
    else:
        whatsapp_message = 'No activity, no numbers were found in saved conversations'

    sendingData = {
        "recipient": '255755888555',
        "text": whatsapp_message
    }
    send_whatsapp_message(sendingData)
    print('=================================')
    print(whatsapp_message)
    print('=================================')
    
def is_valid_message(message):
    text_content = message.get('text', {}).get('body', '').strip()
    return bool(text_content)  # Returns True if there's non-empty text content    

# You'll need to set up a way to periodically call save_inactive_conversations
# This could be done using Django's celery or a custom management command