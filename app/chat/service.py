from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from app.llm.model import create_model


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

        # Temporary in-memory conversation storage.
        # Redis can replace this later.
        self.conversations: dict[str, list[BaseMessage]] = {}

    async def chat(
        self,
        conversation_id: str,
        user_message: str,
    ) -> str:

        # Get existing conversation history.
        history = self.conversations.get(conversation_id, [])

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *history,
            HumanMessage(content=user_message),
        ]

        # Ask the LLM.
        response = await self.model.ainvoke(messages)

        # Extract response text.
        response_text = self._extract_text(response)

        # Save the conversation.
        history.append(HumanMessage(content=user_message))
        history.append(AIMessage(content=response_text))

        self.conversations[conversation_id] = history

        return response_text

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