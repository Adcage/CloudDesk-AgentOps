import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AgentMessage, AgentSession


SESSION_MESSAGE_LIMIT = 20


async def load_session(session_id: str, db: Session) -> dict | None:
    session = db.execute(
        select(AgentSession).where(AgentSession.session_id == session_id)
    ).scalar_one_or_none()

    if not session:
        return None

    messages = db.execute(
        select(AgentMessage)
        .where(AgentMessage.session_id == session_id)
        .order_by(AgentMessage.created_at.desc())
        .limit(SESSION_MESSAGE_LIMIT)
    ).scalars().all()

    messages.reverse()

    return {
        "session_id": session.session_id,
        "conversation_id": session.conversation_id,
        "current_agent": session.current_agent,
        "summary": session.summary,
        "messages": [
            {"role": m.role, "content": m.content, "trace_id": m.trace_id}
            for m in messages
        ],
    }


async def save_message(
    session_id: str,
    role: str,
    content: str,
    trace_id: str,
    db: Session,
) -> AgentMessage:
    message = AgentMessage(
        message_id=f"msg_{uuid.uuid4().hex[:12]}",
        session_id=session_id,
        role=role,
        content=content,
        trace_id=trace_id,
    )
    db.add(message)
    db.flush()
    return message


async def create_or_get_session(
    conversation_id: str,
    user_id: str,
    db: Session,
) -> str:
    existing = db.execute(
        select(AgentSession).where(AgentSession.conversation_id == conversation_id)
    ).scalar_one_or_none()

    if existing:
        return existing.session_id

    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    session = AgentSession(
        session_id=session_id,
        conversation_id=conversation_id,
        user_id=user_id,
    )
    db.add(session)
    db.flush()
    return session_id