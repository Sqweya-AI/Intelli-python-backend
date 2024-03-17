# bot_app/urls.py
from django.urls import path
from .views import AnalyseView, chat, translate

urlpatterns = [
    path('', chat, name='chat'),
    path('translate', translate, name='translate'),
    path('analyse', AnalyseView.as_view(), name='analyse'),
]
