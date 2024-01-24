import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login, logout

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        
        self.user = (self.scope['user'])

        # establish the connection
        await self.accept('Token')

    async def disconnect(self, close_code):

        # leave the room
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """Central function that handles all incoming message traffic"""

        # recieving the data from the websocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type_msg = (text_data_json['type'])
        # send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': type_msg,
                'message': message
            }
        )

    async def chat_message(self, event):
        # recieve the message from any other members of the groups
        
        message = event['message']

        # send the message to the recieving consumer websocket
        await self.send(text_data=json.dumps({"message": message}))
