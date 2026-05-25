from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    __table_args__ = {"schema": "agent"}

    session_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(50))
    current_agent: Mapped[str | None] = mapped_column(String(50))
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AgentMessage(Base):
    __tablename__ = "agent_messages"
    __table_args__ = {"schema": "agent"}

    message_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class AgentTrace(Base):
    __tablename__ = "agent_traces"
    __table_args__ = {"schema": "agent"}

    trace_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    session_id: Mapped[str | None] = mapped_column(String(50))
    user_query: Mapped[str | None] = mapped_column(Text)
    selected_agent: Mapped[str | None] = mapped_column(String(100))
    intent: Mapped[str | None] = mapped_column(String(100))
    risk_level: Mapped[str | None] = mapped_column(String(20))
    entities: Mapped[dict | None] = mapped_column(JSONB)
    model_used: Mapped[str | None] = mapped_column(String(100))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    token_usage: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    approval_required: Mapped[bool | None] = mapped_column(Boolean, server_default="false")
    approval_id: Mapped[str | None] = mapped_column(String(50))
    handoff_count: Mapped[int | None] = mapped_column(Integer, server_default="0")
    citations: Mapped[dict | None] = mapped_column(JSONB)
    workflow_steps: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str | None] = mapped_column(String(50), server_default="running")
    final_answer: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class AgentToolCall(Base):
    __tablename__ = "agent_tool_calls"
    __table_args__ = {"schema": "agent"}

    tool_call_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(100))
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_input: Mapped[dict | None] = mapped_column(JSONB)
    tool_output: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str | None] = mapped_column(String(50), server_default="success")
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class AgentHandoff(Base):
    __tablename__ = "agent_handoffs"
    __table_args__ = {"schema": "agent"}

    handoff_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False)
    from_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    to_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    handoff_payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class AgentMemory(Base):
    __tablename__ = "agent_memory"
    __table_args__ = {"schema": "agent"}

    memory_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_type: Mapped[str | None] = mapped_column(String(50))
    subject_id: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "agent"}

    document_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str | None] = mapped_column(String(50), server_default="policy")
    source_path: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(String(50), server_default="1")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = {"schema": "agent"}

    chunk_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding = mapped_column(Vector(1024), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class EvalCase(Base):
    __tablename__ = "eval_cases"
    __table_args__ = {"schema": "agent"}

    case_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_doc: Mapped[str | None] = mapped_column(String(255))
    expected_tools: Mapped[str | None] = mapped_column(Text)
    expected_action: Mapped[str | None] = mapped_column(String(100))
    risk_level: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class EvalResult(Base):
    __tablename__ = "eval_results"
    __table_args__ = {"schema": "agent"}

    result_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(100))
    retrieval_hit: Mapped[bool | None] = mapped_column(Boolean)
    tool_call_correct: Mapped[bool | None] = mapped_column(Boolean)
    approval_routing_correct: Mapped[bool | None] = mapped_column(Boolean)
    task_success: Mapped[bool | None] = mapped_column(Boolean)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    detail: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class AgentCostDetail(Base):
    __tablename__ = "agent_cost_details"
    __table_args__ = {"schema": "agent"}

    cost_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_type: Mapped[str | None] = mapped_column(String(100))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
