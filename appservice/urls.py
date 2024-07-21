from .views import *
from django.urls import path


urlpatterns = [
    path('webhook/', webhook),
    path('conversations/whatsapp/chat_sessions/<str:phone_number>/', chatsessions_history),
    path('conversations/whatsapp/chat_sessions/<str:phone_number>/<str:customer_number>/', messages_history),
    path('conversations/whatsapp/send_message/', webhook),
    path('conversations/whatsapp/takeover_conversation/', takeover),
    path('conversations/whatsapp/handover_conversation/', handover),
    path('list/<str:owner>/', appservices_list),
]