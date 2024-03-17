# auth_app/managers.py
from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    def create_hotel_manager(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_hotel_manager', True)
        return self._create_user(username, email, password, **extra_fields)
    
    def create_staff(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self._create_user(username, email, password, **extra_fields)


