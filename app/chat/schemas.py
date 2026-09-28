from pydantic import BaseModel

class ChatRequest(BaseModel):
    conversationId: str
    message: str


class ChatResponse(BaseModel):
    response: str