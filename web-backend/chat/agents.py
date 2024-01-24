from abc import ABC, abstractmethod

class ChatAIAgent(ABC):
    """
        Abstract class ised to define the interface of the chat AI agent.
    """
    
    
    def __init__(self, model, vector_store, *args, **kwargs):
        """
        Constructor to instatiate the chat AI agent

        @param: the LangChaint chat AI model
        """
        pass
    
    @abstractmethod
    def apply_prompt(self, question:  str = None):
        """Define a dynamic LangChain prompt pipeline

        @param: question: the question to be answered (optional)

        @returns a LangChain Pipeline instance
        """
        pass
    
    @abstractmethod
    def retrieve_relevant_docs(self, question):
        """
        Retrieve relevant documents from the configured vector database

        @question: the raw text of question used
        """
        pass

    @abstractmethod
    def get_chat_history(self, user_id: int):
        """
        Get the chat history of the user

        @returns a LangChain ChatPrompTemplate instance
        """
        pass
    
    @abstractmethod
    def answer(self, question):
        """
        Answer a question using the LangChain chat AI model
        and configured setup including prompts and vector database

        @param: question: the question to be answered
        """
        pass