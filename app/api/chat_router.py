from fastapi import APIRouter, HTTPException
import secrets

from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatService


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

chat_service = ChatService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversationId
    if conversation_id is None:
        conversation_id = secrets.token_urlsafe(32)
    # verify that the conversation still exists.
    else:
        exists = await chat_service.conversation_exists(conversation_id)
        if not exists:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or expired.",
            )
    response = await chat_service.chat(
        conversation_id=request.conversationId,
        user_message=request.message
    )

    return ChatResponse(
        conversationId=conversation_id,
        response=response
    )

