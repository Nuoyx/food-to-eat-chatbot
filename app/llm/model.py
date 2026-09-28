import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def create_model() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = "gemini-3.8-flash"

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        max_retries=2,
    )

