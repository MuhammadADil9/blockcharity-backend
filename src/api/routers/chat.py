from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.chat_service import ChatService

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    role: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    try:
        service = ChatService()
        reply = service.chat(message=body.message, role=body.role)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
