# main_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home-page'),
    path('home/', HomePageView.as_view(), name='home-page'),
    path('reservations/', ReservationAPIView.as_view(), name='reservations'),
    path('reservations/<int:pk>/', ReservationAPIView.as_view(), name='reservation-detail'),
    path('waitlist/', WaitlistMemberAPIView.as_view(), name='waitlist'),
]