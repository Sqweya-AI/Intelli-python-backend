# auth_app/admin.py
from django.contrib import admin
from .models import User

admin.site.register(User)
