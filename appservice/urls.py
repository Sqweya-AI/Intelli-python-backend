from .views import *
from django.urls import path


urlpatterns = [
    path('webhook/', webhook),
    path('conversations/whatsapp/chat_sessions', chatsessions_history),
    path('conversations/whatsapp/send_message', webhook),
    path('conversations/whatsapp/takeover_conversation/', takeover),
    path('conversations/whatsapp/handover_conversation/', handover),
]