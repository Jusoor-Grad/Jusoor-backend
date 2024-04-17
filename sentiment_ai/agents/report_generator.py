


from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAI, OpenAIEmbeddings
from authentication.models import User
from chat.agents import AIAgent
from chat.models import ChatMessage
from jusoor_backend.settings import env
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from sentiment_ai.types import SentimentReportAgentResponseFormat
from django.db.models import Q


class SentimentReportGenerator(AIAgent):

    def __init__(self, model = OpenAI, metadata_index: str = "reports", model_name: str = 'gpt-3.5-turbo-1106', embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 20, collection_name: str = env('EMBEDDING_COLLECTION_NAME')):
        
        self.llm_model = model(openai_api_key=env('OPENAI_KEY'))
        self.history_len = history_len
        self.metadata_index = metadata_index


    def _retrieve_history(self, user: User):
        """
            retrireve up to 20 messages from last exchanged message
        """

        user_messages = ChatMessage.objects.filter(
            (Q(sender=user) | Q(receiver=user)))
        history = user_messages\
        .order_by('created_at')[:min(self.history_len, user_messages.count())]

        formatted_messages = []

        for msg in user_messages:

            if msg.sender.id == user.id:
                formatted_messages.append("<patient-message>{patient_message}</patient-message>".format(patient_message=msg.content))
            else:
                formatted_messages.append("<expert-message>{expert_message}</expert-message>".format(expert_message=msg.content))

        return "<covnersation>" + "\n".join([message.content for message in history]) + "</conversation>"


    def _construct_prompt(self, user: User):
        """
            construct a prompt for the sentiment analysis model
        """
        history = self._retrieve_history(user)
        prompt = PromptTemplate.from_template("""
        You are professional mental health expert called Eve. You are tasked with generating an extnesive report
        about the mental health patient you chatted with in the past. His username is {username}.
        Make the report in an expert style and professional writing. Be gentle but without dismissing obvious mental health facts
        noticed about your past conversation to maximize the value for the patient. This report will be viewed by the patient himself
        and will be used to help him understand his mental health status and take the necessary actions, so speak to the patient directly
        in your report

        NOTE: the conversation can be in either Arabic or English. Make sure to handle both languages in your analysis. To make it easier for you,
        use only English in the report output

        The following is the chat history of your past conversation with the patient, which you will use to generate the report:
        
        {history}
        
        The output needs to be in the following format:
        the patient in the chat history. With highlights of some possibility of mental health issues that you are highly confident about.
        - Conversation Highlights: A summary of the most important points of the conversation. Areas of concern about the patient.
        - Recommendations: Your advice and recommendations for the patient based on the conversation and analysis results. Emphasis to schedule an appointment if the case requires attention.

        Make sure to make the requested outputs suitable to be in JSON format. ONLY PROVIDE TWO KEYS: "conversation_highlights" and "recommendations" WITH A TEXT VALUE FOR EACH KEY
        DO NOT UNDER ANY CIRUCMSTANCES PROVIDE EXTRA KEYS OR DIFFERENT KEYS IN THE SPECIFIED OUTPUT FORMAT
        """)
        return prompt.invoke({"history": history, "username": user.username})

    @property
    def output_parser(self):
        """
            structure of the output coming from the sentiment report
        """
        return PydanticOutputParser(pydantic_object=SentimentReportAgentResponseFormat)

    def answer(self, user: User, messages: List[ChatMessage]):
        """
            generate a sentiment report for the patient based on the exchanged messages
        """
        
        prompt = self._construct_prompt(user)
        
        chain =  self.llm_model | self.output_parser

        print('MODEL NAME: ', self.llm_model.model_name)

        return chain.invoke(prompt)

def run():
    agent = SentimentReportGenerator()
    user = User.objects.get(pk=137)
    messages = ChatMessage.objects.all()
    response = agent.answer(user, messages)
    print(response)