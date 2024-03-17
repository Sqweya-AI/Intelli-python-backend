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

openai.api_key = api_key
# LLM_model = "gpt-3.5-turbo"
LLM_model = "gpt-4"

# chat view
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
    try:
        response = openai.chat.completions.create(
            model=LLM_model,
            messages=[
                {"role": "system", "content": "You are hotel's customer service worker. You are receiving enquiries from customers and handling them. The name of the hotel you are working for is Hunters Royal Hotel . Use the data you are already aware of relating to the Hunters Royal Hotel, located in Ghana. Your response should be in the same language the client has contacted the hotel in (e.g if a customer speaks to you in swahili, reply in swahili, english for english .etc)"},
                {"role": "user", "content": user_input},
            ],
            max_tokens=256,
            temperature=0.5
        )
        return Response({
            "request": "Fun chat",
            "input": user_input,
            "response": response.choices[0].message.content
            })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=500)

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
            "request": "translate",
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
                    "request": "analyse",
                    "input": user_input,
                    "response": analysis_response,
                    "analysis_id": serializer.instance.id  # Including the ID
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({
                    "error": f"Error during analysis: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









# old translate view/ nod db saving
# #analyse view
# @api_view(['POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([]) 
# def analyse(request):
#     """
#     Handle analysis requests.

#     Parameters:
#     - user_input: The user's input for analysis.

#     Returns:
#     - Response containing the analysis request details and response.
#     """
#     user_input = request.data.get('user_input')
#     try:
#         response = openai.chat.completions.create(
#             model=LLM_model,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a helpful assistant. Analyse the prompt you receive and provide what conclusion you draw, as to what is the 1.Mood and 2.Feeling of the user who provided the input/query"
#                 },

#                 {
#                     "role": "user",
#                     "content": user_input
#                 },
#             ],
#             max_tokens=256,
#             temperature=0.5
#         )
#         return Response({
#             "request": "analyse",
#             "input": user_input,
#             "response": response.choices[0].message.content
#         })
#     except Exception as e:
#         return Response({
#             "error": str(e)
#         }, status=500)