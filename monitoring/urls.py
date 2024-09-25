from .views import *
from django.urls import path

urlpatterns = [
    path('sentiment_analysis/', sentiment_analysis),
]