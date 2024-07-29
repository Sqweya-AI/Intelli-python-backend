# myapp/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'events'

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_event(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
