"""
File to store all DTO types for auth app
"""

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    refresh: str = Field(min_length=1)
    access: str = Field(min_length=1)