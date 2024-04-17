from abc import ABC, abstractmethod
from pyexpat import model
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from authentication.models import User
from chat.models import ChatMessage
from jusoor_backend.settings import env
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from jusoor_backend.settings import env
from django.db.models import Q
# from langchain.cache import SQLiteCache
# from langchain.globals import set_llm_cache

# set_llm_cache(SQLiteCache(database_path="langchain.db"))

class AIAgent(ABC):
    """
        Abstract class ised to define the interface of the chat AI agent.
    """
    
    
    def __init__(self, 
    model, 
    metadata_index: str,
    embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 8 , collection_name: str = env('EMBEDDING_COLLECTION_NAME') , *args, **kwargs):
        """
        Constructor to instatiate the chat AI agent

        @param: chat_model the LangChaint chat AI model
        @param: embeddings the LangChain embeddings model
        """
        pass
    
    def _retrieve_history(self, user: User):
        """
            retrieve the chat history of the user in the chatroom

            @param: user_id: the id of the user
            @param: chatroom_id: the id of the chatroom
        """

    def _construct_prompt(self):
        """Define a dynamic LangChain prompt pipeline

        @param: question: the question to be answered (optional)

        @returns a LangChain Pipeline instance
        """
        pass
    
    




class ChatGPTAgent(AIAgent):


    def __init__(self, 
        prompt: str,
        chat_model: BaseChatModel = ChatOpenAI,
        model_name: str = 'gpt-3.5-turbo', 
        history_len: int = 8, 
        embeddings: Embeddings = OpenAIEmbeddings, 
        collection_name: str = env('EMBEDDING_COLLECTION_NAME'),
        metadata_index: str = 'chat',
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
        self.temperature = float(temperature)
        self.top_p = float(top_p)
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

    def _retrieve_history(self, user: User) -> List[HumanMessagePromptTemplate | AIMessagePromptTemplate]:
        
        # getting the message history
        
        user_messages = ChatMessage.objects.filter(
            (Q(sender=user) | Q(receiver=user)))

        history = user_messages\
        .order_by('created_at')[:min(self.history_len, user_messages.count())]


    
        # inject messages into prompt
        messages = []
        for message in history:
            if message.sender.id == user.pk:
                messages.append(HumanMessagePromptTemplate.from_template(message.content))
            else:
                messages.append(AIMessagePromptTemplate.from_template(message.content))

        return messages

    def _construct_prompt(self, user: User,  message: str):
        
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
        
        history_messages = self._retrieve_history(user)

        incoming_message = HumanMessagePromptTemplate.from_template('{user_input}')
        return ChatPromptTemplate.from_messages(
            [
            system_prompt,
            *history_messages,
            incoming_message
        ]
        )

    def _construct_few_shots(self, message: str):
        """
            constructing a few shot prompt for the AI model using an RAG setup
        """

        # TODO: needs further understandin
        reference_documents = self.vector_store.similarity_search(message, k=1)

        formatted_docs = [
            """<patient>
                    {patient_message}
               </patient> 
            <therapist>
                    {therapist_message}
            </therapist>
            """.format(patient_message=doc.page_content, therapist_message=doc.metadata['response']) for doc in reference_documents
        ]

        return """
                    The following are references recorded from specialized mental health personnel who conducted mental health conversations like yours. Use
                    them as a reference on how to answer your patient. Do not stick to same wording, but use similar techniques to communicate.

                    <list>
                    {messages}
                    </list>
                """.format(messages="\n".join(formatted_docs))

    def answer(self, user: User, message: str):
        
        # 1. get history and reference prompting
        chat_template = self._construct_prompt(user=user, message=message)
        # TODO: use a filter to restrict lookup to only chat metadata tags
        
        reference_message = self._construct_few_shots(message)
        

        messages = chat_template.format_messages(
            user_input=message,
            reference_message= reference_message
        )

        return self.chat_model.invoke(messages, temperature= self.temperature, top_p= self.top_p)

class DummyAIAgent(AIAgent):

    def __init__(self, chat_model: BaseChatModel = ChatOpenAI, embeddings: Embeddings = OpenAIEmbeddings, history_len: int = 8, collection_name: str = env('EMBEDDING_COLLECTION_NAME'), *args, **kwargs):
        super().__init__(chat_model, embeddings, history_len, collection_name, *args, **kwargs)

    def answer(self, user_id: int, message: str):
        return "I am a dummy agent. I am not configured to answer questions yet."