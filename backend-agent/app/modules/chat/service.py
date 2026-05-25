import logging

from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.workflow.graph import execute_workflow

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        logger.info(f"Processing chat request: trace_id={request.trace_id}")
        result = await execute_workflow(request, self.db)
        return result