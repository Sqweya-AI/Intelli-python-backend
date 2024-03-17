# users/views.py
from datetime import timedelta
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from .utils import send_reset_password_email, send_verification_email
import uuid
from django.utils import timezone


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # SKIP CSRF check
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Bypass csrf check for login and register actions

    #permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]  # Use JWTAuthentication for all actions

    # REGISTER
    @action(detail=False, methods=['post'])
    def register(self, request):
        email = request.data.get("email")
        role = request.data.get("role")
        password = request.data.get("password")
        email_verification_token = uuid.uuid4().hex  # Generate a verification token

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # Create a new user with verification token
        new_user = User.objects.create(
            username=email,
            email=email,
            role=role,
            email_verification_token=email_verification_token,
        )
        new_user.set_password(password)
        new_user.save()

        # Send verification email
        send_verification_email(email, email_verification_token)
        serializer = UserSerializer(new_user, many=False)
        return Response({"message": "Account successfully created", "data": serializer.data, "verification_token": email_verification_token},  status=status.HTTP_201_CREATED)

    # VERIFY EMAIL
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_email(self, request):
        email = request.data.get('email')
        email_verification_token = request.data.get('email_verification_token')
        user = User.objects.filter(email=email).first()
        if user:
            if user.email_verification_token == email_verification_token:
                if user.is_email_verified:
                    return Response({'message': 'Email already confirmed'}, status=status.HTTP_200_OK)
                user.is_email_verified = True
                user.save()
                return Response({'message': 'Success! email verified'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Email not registered, Redirect to register'}, status=status.HTTP_400_BAD_REQUEST)

    # LOGIN
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(username=email).first()
        if user is not None:
            current = authenticate(username=email, password=password)
            if current is not None:
                login(request, current)
                refresh = RefreshToken.for_user(user)
                return Response({'access_token': str(refresh.access_token), 'refresh_token': str(refresh)})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # FORGOT PASSWORD
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            reset_token = uuid.uuid4()  
            token_expiry = timezone.now() + timedelta(seconds=40) #Expiry time duration
            user.reset_token = reset_token
            user.reset_token_expiry = token_expiry
            user.save()
            send_reset_password_email(user.email, str(reset_token))  # Convert UUID to string for sending in the email
            return Response({'message': f'Reset link has been sent to your email.', "link": f'http://localhost:8000/auth/forgot_password/{str(reset_token)}'})
        return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    

    #RESET PASSWORD
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request, reset_token=None):
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        try:
            reset_token = uuid.UUID(reset_token)
            user = User.objects.filter(reset_token=reset_token).first()
        except (User.DoesNotExist, ValueError):
            # Invalid or expired reset token
            return Response({'error': 'Invalid or expired reset token.', "Reality":"INVALID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user is not None:
            if user.is_reset_token_valid():
                user.set_password(new_password)
                user.reset_token = None
                user.reset_token_expiry = None
                user.reset_token_used_already = True
                user.save()
                return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
            # Reset token has expired
            return Response({'error': 'Reset token has expired.',  "Reality":"EXPIRED"}, status=status.HTTP_400_BAD_REQUEST)
        # Reset token already used
        return Response({'error': 'Invalid or expired reset token.', "Reality":"USED"}, status=status.HTTP_400_BAD_REQUEST) 

    # CHANGE PASSWORD
    @csrf_exempt
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Update user's password if old password is correct and user is logged in
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)

    # DASHBOARD
    @csrf_exempt
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role == 'manager':
            return Response({'message': 'Dashboard data for  hotel manager ONLY'})
        return Response({'message': 'You do not have permission to access the dashboard'}, status=403)
    
    # PROFILE
    @csrf_exempt
    @action(detail=False, methods=['get'])
    def profile(self, request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # RESERVATIONS
    @action(detail=False, methods=['get'])
    def reservations(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if user.role in ['manager', 'customer_service']:
            return Response({'message': 'Reservations data for BOTH manager & customer service'})
        return Response({'message': 'You do not have permission to access reservations'}, status=403)
    
    # REFRESH TOKEN
    @csrf_exempt
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh_token(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)
                return Response({'access_token': access_token})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
