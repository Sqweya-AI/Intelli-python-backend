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
    

# @api_view(['POST'])
# @authentication_classes([CsrfExemptSessionAuthentication]) 
# def create_reservation(request):
#     serializer = ReservationSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({'message': 'Reservation created successfully'}, status=status.HTTP_201_CREATED)
#     return Response({'error': 'Failed to create reservation', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([CsrfExemptSessionAuthentication]) 
class ReservationAPIView(APIView):
    def post(self, request):
       serializer = ReservationSerializer(data=request.data)
       if serializer.is_valid():
          serializer.save()
          reservation = serializer.data
          return Response({'message': 'Reservation created successfully', "The reservation":reservation}, status=status.HTTP_201_CREATED)
       return Response({'error': 'Failed to create reservation', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        reservations = ReservationModel.objects.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            reservation = ReservationModel.objects.get(pk=pk)
        except ReservationModel.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            reservation = ReservationModel.objects.get(pk=pk)
        except ReservationModel.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)