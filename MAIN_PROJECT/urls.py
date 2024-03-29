# INTELLI_PROJECT/urls.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls')),
    path('auth/', include('auth_app.urls')),
    path('chat/', include('bot_app.urls')),
    path('', include('main_app.urls')), 
]