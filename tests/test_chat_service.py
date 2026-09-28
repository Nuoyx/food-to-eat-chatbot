import pytest

from app.chat.service import ChatService


class FakeResponse:
    content = "How about pizza?"


class FakeModel:

    def __init__(self):
        self.messages = None

    async def ainvoke(self, messages):
        self.messages = messages
        return FakeResponse()


@pytest.mark.anyio
async def test_chat_sends_system_prompt_and_user_message():

    service = ChatService()

    fake_model = FakeModel()
    service.model = fake_model

    response = await service.chat(
        "test-conversation",
        "I want something spicy."
    )

    assert response == "How about pizza?"

    assert len(fake_model.messages) == 2

    assert fake_model.messages[0].type == "system"
    assert fake_model.messages[1].type == "human"

    assert fake_model.messages[1].content == "I want something spicy."

