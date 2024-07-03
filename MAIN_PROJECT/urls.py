# INTELLI_PROJECT/urls.py
from django.contrib import admin
from django.urls import path, include
from bot_app.views import webhook, get_chat_histories


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls')),
    path('auth/', include('auth_app.urls')),
    path('chat/', include('bot_app.urls')),
    path('', include('main_app.urls')), 
    path('webhook/', webhook, name="verify webhook"),
    path('appservice/', include('appservice.urls')),
]