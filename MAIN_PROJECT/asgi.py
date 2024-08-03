"""
ASGI config for MAIN_PROJECT project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN_PROJECT.settings')
django.setup()

# Import routing after Django setup
import notifications.routing
import appservice.routing

channel_layer = get_channel_layer()

async def lifespan(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await channel_layer.flush()
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns +
            appservice.routing.websocket_urlpatterns
        )
    ),
    "lifespan": lifespan,
})