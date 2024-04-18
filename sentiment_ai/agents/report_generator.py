


from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAI, OpenAIEmbeddings
from authentication.models import User
from chat.agents import AIAgent
from chat.models import ChatMessage
from jusoor_backend.settings import env
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers import RetryWithErrorOutputParser, RetryOutputParser
from langchain.prompts import PromptTemplate
from sentiment_ai.enums import FAILED
from sentiment_ai.models import SentimentReport
from sentiment_ai.types import SentimentReportAgentResponseFormat
from django.db.models import Q
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.exceptions import OutputParserException


class SentimentReportGenerator(AIAgent):

    def __init__(self, model = OpenAI, metadata_index: str = "reports" , embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 20, collection_name: str = env('EMBEDDING_COLLECTION_NAME')):
        
        self.llm_model = model(openai_api_key=env('OPENAI_KEY'))
        self.history_len = history_len
        self.metadata_index = metadata_index


    def _retrieve_history(self, user: User):
        """
            retrireve up to 20 messages from last exchanged message
        """

        history = SentimentReport.get_messages_since_last_report(user, max_scope=self.history_len)
        formatted_messages = []

        for msg in history:

            if msg.sender.id == user.id:
                formatted_messages.append("<patient-message>{patient_message}</patient-message>".format(patient_message=msg.content))
            else:
                formatted_messages.append("<expert-message>{expert_message}</expert-message>".format(expert_message=msg.content))

        return "<covnersation>" + "\n".join([message.content for message in history]) + "</conversation>"


    def _construct_prompt(self, user: User, format_instructions: str):
        """
            construct a prompt for the sentiment analysis model
        """

        prompt = PromptTemplate(template="""
        You are professional mental health expert called Eve. You are tasked with generating an extnesive report
        about the mental health patient you chatted with in the past. His username is {username}.
        Make the report in an expert style and professional writing. Be gentle but without dismissing obvious mental health facts
        noticed about your past conversation to maximize the value for the patient.

        NOTE: the conversation can be in either Arabic or English. Make sure to handle both languages in your analysis. To make it easier for you,
        use only English in the report output

        The following is the chat history of your past conversation with the patient, which you will use to generate the report:
        
        {history}
        
        The output needs to be in the following format:
        the patient in the chat history. With highlights of some possibility of mental health issues that you are highly confident about.
        - Conversation Highlights: A summary of the most important points of the conversation. Areas of concern about the patient.
        - Recommendations: Your advice and recommendations for the patient based on the conversation and analysis results. Emphasis to schedule an appointment if the case requires attention.

        FOLLOW THESE INSTRUCTIONS TO GENERATE THE REPORT JSON OUTPUT:
        {format_instructions}
        """,
        input_variables=["history", "username"],
        partial_variables={"format_instructions": format_instructions},
        )
        return prompt
    @property
    def output_parser(self):
        """
            structure of the output coming from the sentiment report
        """
        return PydanticOutputParser(pydantic_object=SentimentReportAgentResponseFormat)

    def answer(self, user: User)-> SentimentReportAgentResponseFormat:
        """
            generate a sentiment report for the patient based on the exchanged messages
        """
        
        base_parser = self.output_parser
        prompt = self._construct_prompt(user, base_parser.get_format_instructions())
        history = self._retrieve_history(user)
        
        
        # handling incorrect output schema by retrying the requests 2 times
        retry_parser = RetryWithErrorOutputParser.from_llm(parser=base_parser,llm = self.llm_model, max_retries=2)
        completion_chain = prompt |  self.llm_model 

        main_chain = RunnableParallel(
        completion=completion_chain, prompt_value=prompt
    ) | RunnableLambda(lambda x: retry_parser.parse_with_prompt(**x))

        print('MODEL NAME: ', self.llm_model.model_name)

        
        return main_chain.invoke({"history": history, "username": user.username})
        

def run():
    agent = SentimentReportGenerator()
    user = User.objects.get(pk=137)
    messages = ChatMessage.objects.all()
    response = agent.answer(user, report=SentimentReport())
    print(response.conversation_highlights)