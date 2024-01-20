from django.core.management.base import BaseCommand, CommandParser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):

    help = "Send a websocket event to all in channel chat_lobby"



    def add_arguments(self, parser: CommandParser) -> None:
        
        parser.add_argument('--message', '-m', type=str, help="Message to send", required=True)

    def handle(self, *args, **options):

        self.stdout.write(f"Sending a websocket event:  {options['message']}")
     
        # firing a weboskcet event to all subscribed clientd to event chat.message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('chat_lobby',{
            'type': 'chat.message',
            "message": options['message']
        })