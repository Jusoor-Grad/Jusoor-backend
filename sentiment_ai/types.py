from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field

class MessageSentimentRequest(BaseModel):
    id: int
    text: str

class SentimentEval(BaseModel):
    sad: float
    joy: float
    love: float
    fear: float
    anger: float
    surprise: float

class MessageSentimentResponse(BaseModel):
    id: int
    prediction: SentimentEval

class SentimentEvalHttpResponse(BaseModel):
    predictions: List[MessageSentimentResponse]

class SentimentReportAgentResponseFormat(BaseModel):

    conversation_highlights: str = Field(description="A summary of the most important points of the conversation. Areas of concren about the patient")
    recommendations: str = Field(description="Recommendations for the patient based on the conversation and analysis results. Emphasis to schedule an appointment if the case requires attention")
