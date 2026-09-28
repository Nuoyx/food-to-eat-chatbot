from fastapi import FastAPI

from app.api.chat_router import router as chat_router

app = FastAPI(
    title="Food To Eat Chatbot",
    version="1.0.0",
)

app.include_router(chat_router)

@app.get("/")
def main():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
