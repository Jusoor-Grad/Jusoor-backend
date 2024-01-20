import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):

    def connect(self):

        # persist the data for the consumer connection
        # to use it for group sending
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # join group name
        async_to_sync(
            self.channel_layer.group_add
        )(
            self.room_group_name, self.channel_name
        )
        # establish the connection
        self.accept()

    def disconnect(self, code):
        
        # skidadle from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None):
        # extracting the incoming JSON string form the connected client
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # sending back a response, can be our chatbot for example
        # self.send(text_data=json.dumps({
        #     "message": message
        # }))

        # we sending to groups now through the channel layer big boys
        async_to_sync(
            self.channel_layer.group_send
        )(
            self.room_group_name, {
                'type': "chat.message", ## calling the chat_message function
                'message': message
            }
        )

    def chat_message(self, event):
        # recieving any event with type chat.message for all affected consumer

        message = event['message']

        # send to the websocket
        self.send(text_data=json.dumps({"message": message}))

