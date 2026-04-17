from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Message(BaseModel):
    role: str
    content: str
    time: Optional[datetime] = None


class ConversationContext(BaseModel):
    city: Optional[str] = None
    weather: Optional[str] = None
    last_intent: Optional[str] = None


class Conversation(BaseModel):
    id: str
    user_id: str
    session_id: str
    messages: List[Message] = []
    context: Optional[ConversationContext] = None
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    outfit_name: Optional[str] = None
    items: list = []
    outfit_image: Optional[str] = None
    template: Optional[str] = None
    message: Optional[str] = None


class SearchRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None


class SearchResponse(BaseModel):
    keyword: str
    filters: dict = {}
    items: list = []
    total: int = 0
