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

#Reservation creation and viewing
@authentication_classes([CsrfExemptSessionAuthentication]) 
class ReservationAPIView(APIView):
    def post(self, request):
       serializer = ReservationSerializer(data=request.data)
       if serializer.is_valid():
          serializer.save()
          reservation = serializer.data
          return Response({'message': 'Reservation created successfully', "The reservation":reservation}, status=status.HTTP_201_CREATED)
       return Response({'error': 'Failed to create reservation', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

#Waitlist joining and viweing
@authentication_classes([CsrfExemptSessionAuthentication]) 
class WaitlistMemberAPIView(APIView):
    def post(self, request):
       serializer = WaitlistMemberSerializer(data=request.data)
       if serializer.is_valid():
          serializer.save()
          waitlist_member = serializer.data
          return Response({'message': 'Waitlist member created successfully', "The waitlist member":waitlist_member}, status=status.HTTP_201_CREATED)
       return Response({'error': 'Failed to create waitlist member', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        waitlist_members = WaitlistMember.objects.all()
        serializer = WaitlistMemberSerializer(waitlist_members, many=True)
        return Response(serializer.data)