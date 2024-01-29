from cgitb import text
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login, logout
from .agents import ChatGPTAgent
class ChatConsumer(AsyncWebsocketConsumer):
    """
        Class used to handle incoming messages from students
        and replies back with chatbot streamed response
    """

    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = (self.scope['user'])
        self.room_group_name = f'user_{(self.user.pk)}'

        

        # join room group
        await self.channel_layer.group_add(
            f'user_{(self.user.pk)}', self.channel_name
        )
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
        print('RECIEVED DATA', text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': text_data_json['type'],
                'message': message
            }
        )

    async def chat_message(self, event):
        # recieve the message from any other members of the groups
        print('AHHHH')
        message = event['message']

        chat_agent=  ChatGPTAgent()

        
        await self.send(text_data=json.dumps({"message": "START", 'type':'chat.message_start'}))

        async for chunk in chat_agent.answer(self.user.pk, message):
            # send the message to the recieving consumer websocket
            await self.send(text_data=json.dumps({"message": chunk.content, 'type':'chat.message_content'}))

        await self.send(text_data=json.dumps({"message": "Chatbot has left the chat", 'type':'chat.message_end'}))
