# your_app_name/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/messages/', consumers.MessageConsumer.as_asgi()),
]

"""
uvicorn MAIN_PROJECT.asgi:application --host 0.0.0.0 --port 8000
"""