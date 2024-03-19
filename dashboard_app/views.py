# # dashboard/views.py
from auth_app.models import User
from auth_app.serializers import UserSerializer
from .serializers import *
from rest_framework.decorators import action
from rest_framework import viewsets, status
from .models import AgentRole, Agent, ContactChannel, DashboardModel
from .serializers import AgentRoleSerializer, AgentSerializer, ChannelSerializer, DashboardModelSerializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # SKIP CSRF check

class DashboardModelViewSet(viewsets.ModelViewSet):
    queryset = DashboardModel.objects.all()
    serializer_class = DashboardModelSerializer
    authentication_classes = [CsrfExemptSessionAuthentication] # to disable csrf check

    def list(self, request):#to return the list of customer service agents instead of the default queryset = DashboardModel.objects.all()
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = User.objects.filter(role='customer_service')
        serializer = UserSerializer(queryset, many=True) 
        return Response({"Content":"All registered customer service agents", "The list":serializer.data}, status=status.HTTP_200_OK)
    
    # RESERVATIONS
    @action(detail=False, methods=['get'])
    def reservations(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            return Response({'message': 'Reservations data for BOTH manager & customer service'})
        return Response({'message': 'You do not have permission to access reservations'}, status=403)
    
    # OVERVIEW
    @action(detail=False, methods=['get'])
    def overview(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role == 'manager':
            return Response({'content': 'Dashboard Overview data', "User Role": 'HOTEL MANAGERS only'},status=status.HTTP_200_OK)
        if request.user.role == 'customer_service':
            return Response({'content': 'Dashboard Overview data', "User Role": 'CUSTOMER SERVICE AGENTS only'},status=status.HTTP_200_OK)
        return Response({'message': 'User not allowed to access dashboard overview'}, status=403)
    
    # BILLING
    @action(detail=False, methods=['get'])
    def billing(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role == 'manager':
            return Response({'content': 'Billing data', "User Role": 'HOTEL MANAGERS only'}, status=status.HTTP_200_OK)
        return Response({'message': 'User not allowed to access the billing'}, status=403)

    # SETTINGS
    @action(detail=False, methods=['get', 'put'])
    def setting(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role == 'manager':
            if request.method == 'PUT':
                return Response({'content': 'Updated Settings data', "Settings type": 'Managers settings UPDATE done'}, status=status.HTTP_200_OK)
            return Response({'content': 'Current Settings data', "Settings type": 'Managers  CURRENT settings'}, status=status.HTTP_200_OK)
        if request.user.role == 'customer_service':
            if request.method == 'PUT':
                return Response({'content': 'Updated Settings data', "Settings type": 'AGENTS settings UPDATE done'}, status=status.HTTP_200_OK)
            return Response({'content': 'Current Settings data', "Settings type": 'AGENTS  CURRENT settings'}, status=status.HTTP_200_OK)

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

class AgentRoleViewSet(viewsets.ModelViewSet):
    queryset = AgentRole.objects.all()
    serializer_class = AgentRoleSerializer

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = ContactChannel.objects.all()
    serializer_class = ChannelSerializer

    @action(detail=False, methods=['post'])
    def add_channel(self, request):
        # Implement the logic for adding a new channel
        return Response({'message': 'Add Channel API'})

    @action(detail=True, methods=['delete'])
    def delete_channel(self, request, pk=None):
        # Implement the logic for deleting a channel
        return Response({'message': 'Delete Channel API'})