from django.core.management.base import BaseCommand, CommandParser
import boto3
import json
from pprint import pprint
from jusoor_backend.settings import env

class Command(BaseCommand):

    help = "make a prediction for the mental disorder classifier deployed on sagemaker"



    def add_arguments(self, parser: CommandParser) -> None:
        pass
        
    def handle(self, *args, **options):

        session = boto3.Session()
        client = session.client("sagemaker-runtime")

        endpoint_name = env("MENTAL_DISORDER_DETECTOR_ENDPOINT")
        content_type = "application/json"
        payload = json.dumps({
            # "inputs": "I cannot focus at all on anything I am not able to finish anything and I am letting my project teammates down",
             "inputs": "I like going out with my friends and playing football",
             "inputs":"I do not like socialising with people at al< I can never get comfortable around people and I always feel like I am being judged",
            "parameters": {
                "return_all_scores": True
            }
        
            })

        response = client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType=content_type,
            Body=payload
        )

        pprint(json.loads(response['Body'].read().decode('utf-8')), compact=True)