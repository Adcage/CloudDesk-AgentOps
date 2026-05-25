from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.chat.schemas import ChatRequest
from app.modules.chat.service import ChatService

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    service = ChatService(db)
    result = await service.handle_chat(request)
    return success_payload(result.model_dump())