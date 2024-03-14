from abc import ABC, abstractmethod
from pyexpat import model
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from chat.models import ChatMessage
from jusoor_backend.settings import env
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from jusoor_backend.settings import env
from django.db.models import Q
# from langchain.cache import SQLiteCache
# from langchain.globals import set_llm_cache

# set_llm_cache(SQLiteCache(database_path="langchain.db"))

class ChatAIAgent(ABC):
    """
        Abstract class ised to define the interface of the chat AI agent.
    """
    
    
    def __init__(self, 
    chat_model: BaseChatModel= ChatOpenAI, 
    embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 8 ,collection_name: str = env('EMBEDDING_COLLECTION_NAME') , *args, **kwargs):
        """
        Constructor to instatiate the chat AI agent

        @param: chat_model the LangChaint chat AI model
        @param: embeddings the LangChain embeddings model
        """
        pass
    
    def _retrieve_history(self, user_id: int, chat_room_id: int):
        """
            retrieve the chat history of the user in the chatroom

            @param: user_id: the id of the user
            @param: chatroom_id: the id of the chatroom
        """

    def _construct_prompt(self, user_id: int, chat_room_id: int, message: str):
        """Define a dynamic LangChain prompt pipeline

        @param: question: the question to be answered (optional)

        @returns a LangChain Pipeline instance
        """
        pass
    
    

    def answer(self, user_id: int, chat_room_id: int, message: str):
        """
        Answer a question using the LangChain chat AI model
        and configured setup including prompts and vector database

        TODO: add params
        """
        pass



class ChatGPTAgent(ChatAIAgent):


    def __init__(self, 
        prompt: str,
        chat_model: BaseChatModel = ChatOpenAI,
        model_name: str = 'gpt-3.5-turbo', 
        history_len: int = 8, 
        embeddings: Embeddings = OpenAIEmbeddings, 
        collection_name: str = env('EMBEDDING_COLLECTION_NAME'),
        temperature: float = 0.9,
        top_p: float = 0.7,
        max_response_tokens: int = 200,
     *args, 
     **kwargs):
        
        # 1. persist the service params
        # TODO: remove hard dependency on env key
        self.max_tokens = max_response_tokens
        self.chat_model = chat_model(model_name= model_name, openai_api_key=env('OPENAI_KEY'))
        self.embeddings = embeddings(openai_api_key=env('OPENAI_KEY'))
        self.history_len = history_len
        self.temperature = temperature
        self.top_p = top_p
        self.prompt = prompt

        # 2. configure the PostgreSQL vector store
        
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            host= env('DB_HOST'),
            port= env('DB_PORT'),
            database= env('DB_NAME'),
            user= env('DB_USER'),
            password= env('DB_PASS'),
            driver='psycopg2'

        )
        self.vector_store = PGVector(
            connection_string= CONNECTION_STRING,
            collection_name= collection_name,
            embedding_function= self.embeddings
        )

        self.retriever = self.vector_store.as_retriever()

    def _retrieve_history(self, user_id: int, chat_room_id: int) -> List[HumanMessagePromptTemplate | AIMessagePromptTemplate]:
        
        # getting the message history
        
        #FIXME: remove the fixed history
        history = ChatMessage.objects.filter(
            (Q(sender__id=user_id) | Q(receiver__id=user_id)) & Q(chat_room__id=chat_room_id))\
        .order_by('-created_at')[:min(self.history_len, ChatMessage.objects.filter(chat_room__id=chat_room_id).count())]

        print
        # inject messages into messages
        messages = []
        for message in history:
            if message.sender.id == user_id:
                messages.append(HumanMessagePromptTemplate.from_template(message.content))
            else:
                messages.append(AIMessagePromptTemplate.from_template(message.content))

        return messages

    def _construct_prompt(self, user_id: int, chat_room_id: int, message: str):
        
        # 1. TODO: retrieve the user message history using his id

        # 2. retrieve most relevant reference messages
       
        guidelines_prompt = self.prompt
        # reference_message = """
        #     To assist you in your respond to patients. The following documents were found to be
        #     relevant to your patient's question based on semnatic similarity of incoming messages:
        #     {reference_message}
        #         """

        full_prompt = guidelines_prompt 

        system_prompt = SystemMessagePromptTemplate.from_template(
            full_prompt)
        
        history_messages = self._retrieve_history(user_id, chat_room_id)
        incoming_message = HumanMessagePromptTemplate.from_template('{user_input}')
        return ChatPromptTemplate.from_messages(
            [
            system_prompt,
            *history_messages,
            incoming_message
        ]
        )


    def answer(self, user_id: int, chat_room_id: int, message: str):
        
        # 1. get history and reference prompting
        chat_template = self._construct_prompt(user_id=user_id, chat_room_id=chat_room_id, message=message)

        reference_messages= self.vector_store.similarity_search(message, k=2)
        
        reference_message = "\n".join([f"- {message}" for message in reference_messages])
        

        messages = chat_template.format_messages(
            user_input=message,
            reference_message= reference_message
        )

        print(chat_template)
        return self.chat_model.invoke(messages, temperature= self.temperature, top_p= self.top_p)

class DummyAIAgent(ChatAIAgent):

    def __init__(self, chat_model: BaseChatModel = ChatOpenAI, embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 8, collection_name: str = env('EMBEDDING_COLLECTION_NAME'), *args, **kwargs):
        super().__init__(chat_model, embeddings, history_len, collection_name, *args, **kwargs)

    def answer(self, user_id: int, chat_room_id: int, message: str):
        return "I am a dummy agent. I am not configured to answer questions yet."