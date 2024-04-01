# main_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home-page'),
    path('home', HomePageView.as_view(), name='home-page'),
    path('make-reservation', create_reservation, name='make-reservation')
]