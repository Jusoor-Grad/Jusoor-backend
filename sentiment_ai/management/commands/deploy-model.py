from django.core.management.base import BaseCommand, CommandParser
from sagemaker.huggingface import HuggingFaceModel
import boto3
import sagemaker
class Command(BaseCommand):

    help = "Send a websocket event to all in channel chat_lobby"



    def add_arguments(self, parser: CommandParser) -> None:
        pass
        
    def handle(self, *args, **options):

        
        sess = sagemaker.Session()

        model = HuggingFaceModel(
            model_data='s3://jusoor-ml-models/mental-disorder-classifier.tar.gz',
            role='SageMakerRole',
            transformers_version="4.26.0",
            pytorch_version="1.13.1",
            py_version="py39"
        )
        
        predictor = model.deploy(
            initial_instance_count=1,
            instance_type="ml.t2.medium"
        )

        data = {
            "inputs": "I am feeling very sad lately that it's making not feel like eating or doing anything at all"
        }

        print(predictor.predict(data))

