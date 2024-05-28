# dashboard_app/views.py
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from auth_app.models import User
from auth_app.utils import send_invite_email
from auth_app.serializers import UserSerializer
from main_app.models import ReservationModel
from rest_framework.permissions import IsAuthenticated, AllowAny
from main_app.serializers import ReservationSerializer
from .serializers import *
from .models import *
from rest_framework.decorators import action
from rest_framework import viewsets, status,views
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from billing_app.views import BillingViewSet
from django.db.models import Q
from django.utils.crypto import get_random_string

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # SKIP CSRF check

class DashboardModelViewSet(viewsets.ModelViewSet):
    queryset = DashboardModel.objects.all()
    serializer_class = DashboardModelSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]

    # EMPLOYEES
    @action(detail=False, methods=['get', 'post'])
    def employees(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role != 'manager':
            return Response({'error': 'Only managers can perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            employees = User.objects.filter(company_name=user.company_name, role='customer_service').order_by('-created_at')
            serializer = UserSerializer(employees, many=True)
            return Response({'employees': serializer.data}, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a 6-digit password
            generated_password = get_random_string(length=6, allowed_chars='0123456789')

            # Prepare the data for creating a new user
            data = {
                'username': email,
                'email': email,
                'role': 'customer_service',
                'company_name': user.company_name,
                'password': generated_password  # Set the generated password here
            }

            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                employee = serializer.save()
                employee.set_password(generated_password)
                employee.is_email_verified = True
                employee.save()
                # Send invite email
                send_invite_email(employee.email, generated_password)

                return Response({'message': f'Employee created successfully and invite email sent. password = {generated_password}'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # RESERVATIONS
    @action(detail=False, methods=['get'])
    def reservations(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        reservations = ReservationSerializer(ReservationModel.objects.all(), many=True).data
        return Response(reservations)
    
    # FILTER RESERVATIONS
    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        reservations = ReservationSerializer(ReservationModel.objects.filter(status='pending'), many=True).data
        return Response(reservations)
    
    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        reservations = ReservationSerializer(ReservationModel.objects.filter(status='confirmed'), many=True).data
        return Response(reservations)
    
    @action(detail=False, methods=['get'])
    def rejected(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        reservations = ReservationSerializer(ReservationModel.objects.filter(status='rejected'), many=True).data
        return Response(reservations)
    
    # OVERVIEW
    @action(detail=False, methods=['get'])
    def overview(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response("OVERVIEW")
    
    
    # SEARCH RESERVATIONS
    @action(detail=False, methods=['get'])
    def search(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        query = request.query_params.get('query', None)
        if not query:
            return Response({'error': 'Search query is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            reservations = ReservationModel.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(customer_email__icontains=query) |
                Q(customer_phone__icontains=query) |
                Q(room_type__icontains=query)
            )
            serializer = ReservationSerializer(reservations, many=True)
            return Response({'message': 'Search results', 'Search Query':query, 'reservations': serializer.data}, status=status.HTTP_200_OK)
        return Response({'message': 'You do not have permission to access reservations.'}, status=status.HTTP_403_FORBIDDEN)
    
    # UPDATE RESERVATION
    @action(detail=False, methods=['post'])
    def update_reservation(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            reservation_id = request.data.get('reservation_id', None)
            if not reservation_id:
                return Response({'error': 'Reservation ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation = ReservationModel.objects.get(id=reservation_id)
            except ReservationModel.DoesNotExist:
                return Response({'error': 'Reservation does not exist.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ReservationSerializer(instance=reservation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Reservation updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'You do not have permission to update reservations.'}, status=status.HTTP_403_FORBIDDEN)
    
    
    # CONFIRM RESERVATION
    @action(detail=False, methods=['post'])
    def confirm_reservation(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            reservation_id = request.data.get('reservation_id', None)
            if not reservation_id:
                return Response({'error': 'Reservation ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation = ReservationModel.objects.get(id=reservation_id)
            except ReservationModel.DoesNotExist:
                return Response({'error': 'Reservation does not exist.'}, status=status.HTTP_404_NOT_FOUND)
            reservation.status = 'confirmed'
            reservation.save()
            return Response({'Success': 'Reservation confirmed.'}, status=status.HTTP_200_OK)
        return Response({'message': 'You do not have permission to confirm reservations.'}, status=status.HTTP_403_FORBIDDEN)

    # REJECT RESERVATION
    @action(detail=False, methods=['post'])
    def reject_reservation(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            reservation_id = request.data.get('reservation_id', None)
            if not reservation_id:
                return Response({'error': 'Reservation ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation = ReservationModel.objects.get(id=reservation_id)
            except ReservationModel.DoesNotExist:
                return Response({'error': 'Reservation does not exist.'}, status=status.HTTP_404_NOT_FOUND)
            reservation.status = 'rejected'
            reservation.save()
            return Response({'Success': 'Reservation rejected.'}, status=status.HTTP_200_OK)
        return Response({'message': 'You do not have permission to reject reservations.'}, status=status.HTTP_403_FORBIDDEN)
    
    # DELETE RESERVATION
    @action(detail=False, methods=['post'])
    def delete_reservation(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager']:
            reservation_id = request.data.get('reservation_id', None)
            if not reservation_id:
                return Response({'error': 'Reservation ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation = ReservationModel.objects.get(id=reservation_id)
                reservation.delete()
                return Response({'Success': 'Reservation deleted'}, status=status.HTTP_200_OK)
            except ReservationModel.DoesNotExist:
                return Response({'error': 'Reservation does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'You do not have permission to delete reservations.'}, status=status.HTTP_403_FORBIDDEN)
    

    # SUBSCRIBE
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        return BillingViewSet.subscribe(self, request)

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = ContactChannelModel.objects.all()
    serializer_class = ChannelSerializer

    @action(detail=False, methods=['post'])
    def add_channel(self, request):
        return Response({'message': 'Add Channel API'})

    @action(detail=True, methods=['delete'])
    def delete_channel(self, request, pk=None):
        return Response({'message': 'Delete Channel API'})
    
class AgentViewSet(viewsets.ModelViewSet):
    queryset = AgentModel.objects.all()
    serializer_class = AgentSerializer

    @action(detail=True, methods=['put'])
    def change_role(self, request, pk=None):
        agent = self.get_object()
        new_role = request.data.get('role')
        if new_role:
            agent.role = new_role
            agent.save()
            return Response({'message': 'Agent role changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'New role not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def supervisors(self, request, pk=None):
        return Response({'message': 'View All Customer Service Supervisor API'})
    
    @action(detail=True, methods=['get'])
    def agents(self, request, pk=None):
        return Response({'message': 'View All Customer Service Agents API'})

class UserSettingsViewSet(viewsets.ModelViewSet):
    queryset = UserSettingsModel.objects.all()
    serializer_class = UserSettingsSerializer
    authentication_classes=[CsrfExemptSessionAuthentication]
    
    # @action(detail=True, methods=['get']) - user specific
    @action(detail=False, methods=['get'])
    def view(self, request, pk=None):
        serializer = UserSerializer(request.user)
        if request.user.is_authenticated:
            return Response({'Data': 'Retrieving Existing Settings Data', "Action": 'User\'s settings UPDATED!', "Account Owner": {"User Email":serializer.data['email'], "User Role":serializer.data['role']}}, status=status.HTTP_200_OK)
        return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # @action(detail=True, methods=['put']) - user specific
    @action(detail=False, methods=['put'])
    def update_settings(self, request, pk=None):
        serializer = UserSerializer(request.user)
        if request.user.is_authenticated:
            return Response({'Data': 'Saving Updated Settings Data', "Action": 'User\'s settings UPDATED!', "Account Owner": {"User Email":serializer.data['email'], "User Role":serializer.data['role']}}, status=status.HTTP_200_OK)
        return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)


# class CreateEmployeeView(views.APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [CsrfExemptSessionAuthentication]

#     def get(self, request, *args, **kwargs):
#         if request.user.role != 'manager':
#             return Response({'error': 'Only managers can view employees.'}, status=status.HTTP_403_FORBIDDEN)
#         employees = User.objects.filter(company_name=request.user.company_name, role='customer_service').order_by('-created_at')
#         serializer = UserSerializer(employees, many=True)
#         return Response({'employees': serializer.data}, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         if request.user.role != 'manager':
#             return Response({'error': 'Only managers can create employees.'}, status=status.HTTP_403_FORBIDDEN)

#         email = request.data.get('email')
#         if not email:
#             return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate a 6-digit password
#         generated_password = get_random_string(length=6, allowed_chars='0123456789')

#         # Prepare the data for creating a new user
#         data = {
#             'username': email,
#             'email': email,
#             'role': 'customer_service',
#             'company_name': request.user.company_name,
#             'password': generated_password  # Set the generated password here
#         }

#         serializer = UserSerializer(data=data)
#         if serializer.is_valid():
#             employee = serializer.save()
#             employee.set_password(generated_password)
#             employee.is_email_verified = True
#             employee.save()
#             # Send invite email
#             send_invite_email(employee.email, generated_password)

#             return Response({'message': f'Employee created successfully and invite email sent. password = {generated_password}'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class HotelSettingsViewSet(viewsets.ModelViewSet):
    queryset = HotelSettingsModel.objects.all()
    serializer_class = HotelSettingsSerializer
    authentication_classes=[CsrfExemptSessionAuthentication]
    
    @action(detail=False, methods=['get'])
    def view(self, request):
        return Response({'message': f'View Hotel Setting API'})

    @action(detail=False, methods=['put'])
    def update_settings(self, request):
        return Response({'message': f'Update Hotel Setting API'})