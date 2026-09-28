from fastapi import APIRouter

from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatService


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

chat_service = ChatService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    response = await chat_service.chat(
        conversation_id=request.conversationId,
        user_message=request.message,
    )

    return ChatResponse(
        response=response
    )

