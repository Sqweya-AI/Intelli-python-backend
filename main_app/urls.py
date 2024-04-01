# main_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home-page'),
    path('home', HomePageView.as_view(), name='home-page'),
    path('reservations', ReservationAPIView.as_view(), name='reservations'),
]