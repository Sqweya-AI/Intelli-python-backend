# users/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid

USER_ROLES = (
    ('manager', 'Hotel Manager'),
    ('customer_service', 'Customer Service'),
    ('customer', 'Customer'),
)

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=USER_ROLES, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    reset_token_expiry = models.DateTimeField(null=True)
    reset_token_used_already = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    
    def is_reset_token_valid(self):
        if self.reset_token_expiry and self.reset_token_expiry > timezone.now():
            return True
        return False

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'role']

    def __str__(self):
        return self.username
    