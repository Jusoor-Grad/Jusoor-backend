
from urllib import response
from chat.models import ChatMessage
from jusoor_backend.settings import env
from requests import post
from typing import List
from sentiment_ai.agents.core import AIPredictor
from sentiment_ai.types import MessageSentimentResponse, SentimentEvalHttpResponse


class EmotionDetector(AIPredictor[str, ChatMessage, MessageSentimentResponse]):
    """ Class used to detect the sentiment of a chat message """

    def __init__(self, identifier: str = env('SENTIMENT_ENDPOINT')) -> None:
        self.endpoint = identifier

    def predict(self, message: ChatMessage) -> MessageSentimentResponse:
            
            # call the http endpoint to get the prediction
            response = SentimentEvalHttpResponse(**post(self.endpoint, json={"messages": [
                {"text": message.content, 'id': message.pk}
            ]}).json())
            print(response.predictions, response.predictions[0])
            return response.predictions[0]

    def batch_predict(self, messages: List[ChatMessage]) -> List[MessageSentimentResponse]:
        
        # call the http endpoint to get the prediction
        response = SentimentEvalHttpResponse(**post(self.endpoint, json={"messages": [
            {"text": message.content, 'id': message.pk} for message in messages
        ]}).json())

        return response.predictions






