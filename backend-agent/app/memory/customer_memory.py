import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AgentMemory, AgentMessage, AgentSession


async def load_customer_memory(customer_id: str, db: Session) -> str:
    try:
        row = db.execute(
            select(AgentMemory)
            .where(
                AgentMemory.subject_type == "customer",
                AgentMemory.subject_id == customer_id,
                AgentMemory.memory_type == "long_term_summary",
            )
            .order_by(AgentMemory.updated_at.desc())
            .limit(1)
        ).scalar_one_or_none()
    except Exception:
        return ""

    return row.content if row else ""


def build_memory_summary_text(
    customer_id: str,
    latest_summary: str,
    session_count: int,
    message_count: int,
) -> str:
    parts = [f"客户 {customer_id} 历史摘要："]
    if latest_summary:
        parts.append(latest_summary.strip())
    if session_count:
        parts.append(f"历史会话数：{session_count}")
    if message_count:
        parts.append(f"已记录消息数：{message_count}")
    return "\n".join(parts).strip()


async def get_memory_summary(customer_id: str, db: Session) -> str:
    latest_summary = await load_customer_memory(customer_id, db)
    try:
        session_count = len(
            db.execute(select(AgentSession).where(AgentSession.user_id == customer_id)).scalars().all()
        )
    except Exception:
        session_count = 0

    try:
        message_count = len(db.execute(select(AgentMessage)).scalars().all())
    except Exception:
        message_count = 0

    if not latest_summary and not session_count and not message_count:
        return ""

    return build_memory_summary_text(
        customer_id=customer_id,
        latest_summary=latest_summary,
        session_count=session_count,
        message_count=message_count,
    )


async def save_customer_memory(
    customer_id: str,
    content: str,
    db: Session,
) -> None:
    try:
        row = db.execute(
            select(AgentMemory).where(
                AgentMemory.subject_type == "customer",
                AgentMemory.subject_id == customer_id,
                AgentMemory.memory_type == "long_term_summary",
            )
        ).scalar_one_or_none()
    except Exception:
        return

    if row:
        row.content = content
    else:
        memory = AgentMemory(
            memory_id=f"mem_{uuid.uuid4().hex[:12]}",
            memory_type="long_term_summary",
            subject_type="customer",
            subject_id=customer_id,
            content=content,
        )
        db.add(memory)
    db.flush()


async def update_memory_from_session(
    customer_id: str,
    session_id: str,
    final_answer: str,
    db: Session,
) -> None:
    messages = db.execute(
        select(AgentMessage)
        .where(AgentMessage.session_id == session_id)
        .order_by(AgentMessage.created_at.desc())
        .limit(6)
    ).scalars().all()

    messages.reverse()
    history_lines = [f"{message.role}: {message.content}" for message in messages]
    history_lines.append(f"assistant: {final_answer}")
    summary = "\n".join(history_lines[-6:])
    await save_customer_memory(customer_id, summary[:2000], db)
