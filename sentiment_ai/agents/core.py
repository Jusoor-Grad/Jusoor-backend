from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from pydantic import BaseModel

AIModelIdentifier = TypeVar('AIModelIdentifier')
AIPredictionFormat = TypeVar('AIPredictionFormat')
AIPredictorInput = TypeVar('AIPredictorInput')

class AIPredictor(Generic[ AIModelIdentifier, AIPredictorInput, AIPredictionFormat]):
    """abstraction to define the interface of an AI predictor 
        with 1-to-1 mapping between input and output"""

    @abstractmethod
    def __init__(self, identifier: AIModelIdentifier) -> None:
        """Constructor to instatiate the AI predictor"""
        pass

    @abstractmethod
    def predict(self, input: AIPredictorInput) -> AIPredictionFormat:
        """Make a prediction using the AI model"""
        pass

    @abstractmethod
    def batch_predict(self, inputs: List[AIPredictorInput]) -> AIPredictionFormat:
        """Make a batch prediction using the AI model"""
        pass