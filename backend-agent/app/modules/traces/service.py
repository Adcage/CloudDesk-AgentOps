import logging

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import AgentHandoff, AgentToolCall, AgentTrace
from app.schemas.trace import TraceDetail, TraceListItem
from app.schemas.tool_calls import ToolCallRecord

logger = logging.getLogger(__name__)


class TraceService:
    def __init__(self, db: Session):
        self.db = db

    def list_traces(self, page: int = 1, page_size: int = 10) -> dict:
        offset = (page - 1) * page_size
        total = self.db.execute(
            select(func.count()).select_from(AgentTrace)
        ).scalar() or 0

        rows = self.db.execute(
            select(AgentTrace)
            .order_by(AgentTrace.created_at.desc())
            .offset(offset)
            .limit(page_size)
        ).scalars().all()

        records = [
            TraceListItem(
                trace_id=t.trace_id,
                session_id=t.session_id or "",
                user_query=t.user_query or "",
                selected_agent=t.selected_agent or "",
                intent=t.intent or "",
                risk_level=t.risk_level or "",
                latency_ms=t.latency_ms or 0,
                approval_required=t.approval_required or False,
                created_at=t.created_at.isoformat() if t.created_at else None,
            )
            for t in rows
        ]

        return {
            "records": [r.model_dump() for r in records],
            "total": total,
            "current": page,
            "size": page_size,
        }

    def get_trace_detail(self, trace_id: str) -> TraceDetail | None:
        trace = self.db.execute(
            select(AgentTrace).where(AgentTrace.trace_id == trace_id)
        ).scalar_one_or_none()

        if not trace:
            return None

        tool_calls_rows = self.db.execute(
            select(AgentToolCall).where(AgentToolCall.trace_id == trace_id)
        ).scalars().all()

        tool_call_records = [
            ToolCallRecord(
                tool_name=tc.tool_name,
                tool_input=tc.tool_input or {},
                tool_output=tc.tool_output,
                status=tc.status or "success",
                latency_ms=tc.latency_ms,
            )
            for tc in tool_calls_rows
        ]

        handoff_rows = self.db.execute(
            select(AgentHandoff).where(AgentHandoff.trace_id == trace_id)
        ).scalars().all()

        handoffs = [
            {
                "from_agent": ho.from_agent,
                "to_agent": ho.to_agent,
                "reason": ho.reason,
                "payload": ho.handoff_payload,
            }
            for ho in handoff_rows
        ]

        handoff_graph = self._build_handoff_graph(handoff_rows)

        return TraceDetail(
            trace_id=trace.trace_id,
            session_id=trace.session_id or "",
            user_query=trace.user_query or "",
            selected_agent=trace.selected_agent or "",
            intent=trace.intent or "",
            risk_level=trace.risk_level or "",
            entities=trace.entities,
            model_used=trace.model_used or "",
            tool_calls=tool_call_records,
            handoffs=handoffs,
            handoff_graph=handoff_graph,
            approval_required=trace.approval_required or False,
            approval_id=trace.approval_id,
            handoff_count=trace.handoff_count or 0,
            citations=trace.citations if isinstance(trace.citations, list) else [],
            workflow_steps=trace.workflow_steps if isinstance(trace.workflow_steps, list) else [],
            final_answer=trace.final_answer or "",
            latency_ms=trace.latency_ms or 0,
            token_usage=trace.token_usage or 0,
            estimated_cost=float(trace.estimated_cost or 0),
        )

    def _build_handoff_graph(self, handoff_rows: list[AgentHandoff]) -> dict | None:
        if not handoff_rows:
            return None

        nodes = []
        edges = []
        seen = set()

        def add_node(agent_name: str):
            if agent_name in seen:
                return
            seen.add(agent_name)
            node_type = "approval" if "approval" in agent_name else "supervisor" if "supervisor" in agent_name else "specialist"
            nodes.append({
                "id": agent_name,
                "label": agent_name.replace("_", " ").title(),
                "type": node_type,
            })

        for row in handoff_rows:
            add_node(row.from_agent)
            add_node(row.to_agent)
            edges.append({
                "from": row.from_agent,
                "to": row.to_agent,
                "reason": row.reason or "",
                "handoff_id": row.handoff_id,
            })

        return {
            "nodes": nodes,
            "edges": edges,
        }
