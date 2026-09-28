from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

import json
from app.core.redis import redis_client
from app.llm.model import create_model
from dotenv import load_dotenv
import os

load_dotenv()
SYSTEM_PROMPT = """
You are the Food To Eat assistant.

Your job is to help users decide what food they want to eat.

You should:
- Be friendly and conversational.
- Help users explore food choices.
- Remember information from the current conversation.
- Use previous conversation context when answering questions.
- Ask useful follow-up questions when appropriate.
- Help users decide between foods.
- Discuss dishes and foods rather than specific restaurants.
- Keep responses concise unless the user asks for more detail.

The user may tell you preferences such as:
- favorite foods
- disliked foods
- ingredients they like
- ingredients they dislike
- cravings
- dietary preferences
- what they ate recently
- what kind of meal they want

Do not claim that you have access to restaurant databases, food databases,
or external APIs unless such functionality has actually been provided to you.

You are currently a conversational food assistant only.
"""


class ChatService:

    def __init__(self):
        self.model = create_model()

        self.conversation_ttl = int(
            os.getenv("CONVERSATION_TTL", "86400")
        )

    @staticmethod
    def _redis_key(conversation_id: str) -> str:
        return f"chat:conversation:{conversation_id}"


    async def chat(
        self,
        conversation_id: str,
        user_message: str,
    ) -> str:

        key = self._redis_key(conversation_id)

        # Load previous conversation history from Redis.
        history = await self._get_history(key)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *history,
            HumanMessage(content=user_message),
        ]

        # Ask the LLM.
        response = await self.model.ainvoke(messages)

        # Extract response text.
        response_text = self._extract_text(response)

        # Save the user's message.
        await self._save_message(
            key,
            HumanMessage(content=user_message),
        )

        # Save the assistant's response.
        await self._save_message(
            key,
            AIMessage(content=response_text),
        )

        return response_text

    async def conversation_exists(
            self,
            conversation_id: str,
    ) -> bool:

        key = self._redis_key(conversation_id)

        return await redis_client.exists(key) > 0

    @staticmethod
    async def _get_history(key: str, ) -> list[BaseMessage]:
        raw_messages = await redis_client.lrange(key, 0, -1)
        history = []
        for raw_message in raw_messages:
            message = json.loads(raw_message)
            if message["type"] == "human":
                history.append(HumanMessage(content=message["content"]))
            elif message["type"] == "ai":
                history.append(AIMessage(content=message["content"]))
        return history

    @staticmethod
    async def _save_message(self, key: str, message: BaseMessage, ):
        data = {"type": message.type, "content": message.content, }
        await redis_client.rpush(key, json.dumps(data))
        await redis_client.expire(key, self.conversation_ttl)

    @staticmethod
    def _extract_text(response) -> str:
        content = response.content
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and item.get("text"):
                    parts.append(item["text"])
            return "".join(parts).strip()
        return str(content).strip()

