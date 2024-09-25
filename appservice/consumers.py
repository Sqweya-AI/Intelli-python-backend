import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.customer_number = self.scope['query_string'].decode().split('customer_number=')[1].split('&')[0]
        self.phone_number = self.scope['query_string'].decode().split('phone_number=')[1]

        self.room_name = f"{self.customer_number}_{self.phone_number}"
        self.room_group_name = f'chat_{self.room_name}'

        print(f"Connecting to group: {self.room_group_name}")  # Debug print

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting from group: {self.room_group_name}")  # Debug print
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        print(f"Received message: {message_content}")  # Debug print

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content
            }
        )

    async def chat_message(self, event):
        message = event['message']
        
        print(f"Sending message: {message}")  # Debug print

        await self.send(text_data=json.dumps(message))