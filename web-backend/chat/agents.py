from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from jusoor_backend.settings import env

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


    def construct_prompt(self, question:  str = None):
        """Define a dynamic LangChain prompt pipeline

        @param: question: the question to be answered (optional)

        @returns a LangChain Pipeline instance
        """
        pass
    
    

    def answer(self, question):
        """
        Answer a question using the LangChain chat AI model
        and configured setup including prompts and vector database

        @param: question: the question to be answered
        """
        pass



class ChatGPTAgent(ChatAIAgent):


    def __init__(self, chat_model: BaseChatModel = ChatOpenAI, history_len: int = 8, embeddings: Embeddings = OpenAIEmbeddings, collection_name: str = env('EMBEDDING_COLLECTION_NAME'), *args, **kwargs):
        
        # 1. persist the service params
        self.chat_model = chat_model
        self.embeddings = embeddings
        self.history_len = history_len

        # 2. configure the PostgreSQL vector store
        
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            host= env('DB_HOST'),
            port= env('DB_PORT'),
            database= env('DB_NAME'),
            user= env('DB_USER'),
            password= env('DB_PASS'),
            port = env('DB_PORT'),
            driver='psycopg2'

        )
        self.vector_store = PGVector(
            connection_string= CONNECTION_STRING,
            collection_name= collection_name,
            embedding_function= self.embeddings
        )

        self.retriever = self.vector_store.as_retriever()

    def construct_prompt(self, user_id: int, question: str = None):
        return super().construct_prompt(question)

    def answer(self, question):
        pass