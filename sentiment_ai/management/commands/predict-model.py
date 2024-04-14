from django.core.management.base import BaseCommand, CommandParser
import tensorflow_text
import tensorflow as tf

class Command(BaseCommand):

    help = "Send a websocket event to all in channel chat_lobby"



    def add_arguments(self, parser: CommandParser) -> None:
        pass
        
    def handle(self, *args, **options):

        reloaded_layer = tf.keras.layers.TFSMLayer('sentiment_ai\emotion_detector-full-model')

        print('RESULT', reloaded_layer(tf.constant(['I am really excited'])))
