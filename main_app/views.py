# main_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from auth_app.views import CsrfExemptSessionAuthentication
from .serializers import *
from rest_framework.decorators import authentication_classes


class HomePageView(APIView):
    def get(self, request):
        return Response({"HOME": "home page"})
    

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication]) 
def create_reservation(request):
    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Reservation created successfully'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Failed to create reservation', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

