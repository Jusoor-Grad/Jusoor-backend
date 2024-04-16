


from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAI, OpenAIEmbeddings
from chat.agents import AIAgent
from chat.models import ChatMessage
from jusoor_backend.settings import env
from langchain_core.output_parsers import PydanticOutputParser

from sentiment_ai.types import SentimentReportAgentResponseFormat



class SentimentReportGenerator(AIAgent):

    def __init__(self, model = OpenAI, metadata_index: str = "reports", embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 20, collection_name: str = ..., *args, **kwargs):
        
        super().__init__(model, metadata_index, embeddings, history_len, collection_name, *args, **kwargs)

    def _retrieve_history(self, user_id: int):
        """
            retrireve up to 20 messages from last exchanged message
        """
        pass

    def _construct_prompt(self, user_id: int, message: str):
        """
            construct a prompt for the sentiment analysis model
        """
        pass

    @property
    def output_parser(self):
        """
            structure of the output coming from the sentiment report
        """
        return PydanticOutputParser(SentimentReportAgentResponseFormat)

    def answer(self, user_id: int, messages: List[ChatMessage]):
        """
            generate a sentiment report for the patient based on the exchanged messages
        """
        pass
