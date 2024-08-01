# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class EventConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_name = 'events'
        
#         # Join group
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
        
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave group
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         pass

#     async def send_event(self, event):
#         await self.send(text_data=json.dumps({
#             'message': event['message']
#         }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # phone_number 
        self.connection_id = self.scope['url_route']['kwargs']['phone_number']
        
        # Créer un nom de canal unique pour cette connexion
        self.user_channel = f"connection_{self.connection_id}"
        
        # Rejoindre le groupe spécifique à cette connexion
        await self.channel_layer.group_add(
            self.user_channel,
            self.channel_name
        )
        
        # Accepter la connexion
        await self.accept()

        # Envoyer l'ID de connexion au client
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'connection_id': self.connection_id
        }))

    async def disconnect(self, close_code):
        # Quitter le groupe spécifique à cette connexion
        await self.channel_layer.group_discard(
            self.user_channel,
            self.channel_name
        )

    async def receive(self, text_data):
        # Gérer les messages entrants si nécessaire
        pass

    async def send_event(self, event):
        print(event)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            # 'appservice': event['appservice'],
            # 'chatsession': event['chatsession']
        }))

    @database_sync_to_async
    def get_user_channel(self, user_id):
        # This method helps to get the user's channel name from a user ID
        return f"user_{user_id}"