from django.urls import path
from .views import sse_view

urlpatterns = [
    path('events/', sse_view, name='sse_view'),
]