# bot_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', chat, name='chat'),
    path('translate', translate, name='translate'),
    path('analyse', AnalyseView.as_view(), name='analyse'),


    path('get_chat_histories/', get_chat_histories, name='get_chat_histories'),
    path('save_chat_history/', save_chat_history, name='save_chat_history'),
]
