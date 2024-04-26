from pprint import pprint
from pydantic import BaseModel, Field
import boto3
import json
from decimal import Decimal
from jusoor_backend.settings import env
from sentiment_ai.agents.core import AIPredictor


class MentalDisorderPrediction(BaseModel):
    """Model to represent the prediction of the mental disorder detector"""

    no_mental_disorder: Decimal
    depression: Decimal
    autism: Decimal
    adhd: Decimal
    anxiety: Decimal
    bipolar: Decimal
    ocd: Decimal



class MentalDisorderDetector(AIPredictor[str, str, MentalDisorderPrediction]):
    """wrapper to predict the mental disorders apparent in a chat message"""

    def __init__(self, identifier: str = env("MENTAL_DISORDER_DETECTOR_ENDPOINT")) -> None:
        
        self.client = boto3.Session().client("sagemaker-runtime")
        self.endpoint_name = identifier

    def _sagemaker_api_call(self, inputs) -> dict:
        """call the sagemaker endpoint to make a prediction"""
        content_type = "application/json"
        payload = json.dumps({
            "inputs": inputs,
            "parameters": {
                "return_all_scores": True
            }
        
        })

        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType=content_type,
            Body=payload
        )

        return json.loads(response['Body'].read().decode('utf-8'))

    def predict(self, input: str) -> MentalDisorderPrediction:

        response = self._sagemaker_api_call(input)[0]

        result = dict()

        for value in response:
            label = value['label'].lower().replace('-', '_')
            score = Decimal(value['score'])
            result[label] = score

        return MentalDisorderPrediction(**result)
    
    def batch_predict(self, inputs: list[str]) -> list[MentalDisorderPrediction]:
            
        response = self._sagemaker_api_call(inputs)

        results = []

        for r in response:
            result = dict()

            for value in r:
                label = value['label'].lower().replace('-', '_')
                score = Decimal(value['score'])
                result[label] = score

            results.append(MentalDisorderPrediction(**result))

        return results

        

    

def run():
    """code to test the business logic using runscript utility"""

    detector = MentalDisorderDetector()

    pprint(detector.predict("I cannot focus at all on anything I am not able to finish anything and I am letting my project teammates down"))
    