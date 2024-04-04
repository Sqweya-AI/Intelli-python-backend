# bot_app/views.py
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.views import APIView
from .serializers import AnalysisSerializer
import openai, os
from dotenv import load_dotenv

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