from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response

import os 

import logging


# Define constants
INACTIVITY_TIMEOUT = 60*60  # 60 seconds for inactivity check
CHECK_INTERVAL = 60*60  # 60 seconds interval for checking

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


def webhook(request):
    if request.method == 'GET':
        print(request.GET)
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
    
    elif request.method == 'POST':
        print(request.data)
        return JsonResponse({'result': request.data}, status=200)
        
