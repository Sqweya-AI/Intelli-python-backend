from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     re_path(r'^ws/events/<str:phone_number>/', consumers.EventConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r'^ws/events/(?P<phone_number>\w+)/$', consumers.EventConsumer.as_asgi()),
]




"""
uvicorn MAIN_PROJECT.asgi:application --host 0.0.0.0 --port 8000
"""