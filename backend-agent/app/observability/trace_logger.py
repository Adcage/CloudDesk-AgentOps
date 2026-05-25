import time
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import AgentHandoff, AgentToolCall, AgentTrace


@dataclass
class StepRecord:
    agent: str
    action: str
    detail: dict | None = None


@dataclass
class ToolCallRecord:
    agent_name: str
    tool_name: str
    tool_input: dict
    tool_output: dict
    latency_ms: int


@dataclass
class HandoffRecord:
    from_agent: str
    to_agent: str
    reason: str
    payload: dict


class TraceLogger:
    def __init__(self, trace_id: str, session_id: str):
        self.trace_id = trace_id
        self.session_id = session_id
        self.start_time = time.time()
        self.steps: list[StepRecord] = []
        self.tool_calls: list[ToolCallRecord] = []
        self.handoffs: list[HandoffRecord] = []

    def log_step(self, agent: str, action: str, detail: dict | None = None):
        self.steps.append(StepRecord(agent=agent, action=action, detail=detail))

    def log_tool_call(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: dict,
        tool_output: dict,
        latency_ms: int,
    ):
        self.tool_calls.append(
            ToolCallRecord(
                agent_name=agent_name,
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=tool_output,
                latency_ms=latency_ms,
            )
        )

    def log_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        payload: dict,
    ):
        self.handoffs.append(
            HandoffRecord(
                from_agent=from_agent,
                to_agent=to_agent,
                reason=reason,
                payload=payload,
            )
        )

    async def save(
        self,
        db: Session,
        final_answer: str,
        model_used: str,
        token_usage: int,
        intent: str | None = None,
        user_query: str | None = None,
        risk_level: str | None = None,
        entities: dict | None = None,
        approval_required: bool | None = None,
        approval_id: str | None = None,
        handoff_count: int | None = None,
        citations: list | None = None,
        workflow_steps: list[dict] | None = None,
        prompt_version: str | None = None,
        selected_agent: str | None = None,
    ) -> None:
        latency_ms = int((time.time() - self.start_time) * 1000)

        from app.observability.cost_tracker import estimate_cost
        estimated_cost = estimate_cost(model_used, token_usage, 0)

        all_steps = workflow_steps or []
        if prompt_version:
            all_steps.append({
                "agent": "versioning",
                "action": "prompt_version_recorded",
                "detail": {
                    "prompt_version": prompt_version,
                    "model_used": model_used,
                },
            })
        for step in self.steps:
            all_steps.append({
                "agent": step.agent,
                "action": step.action,
                "detail": step.detail,
            })

        trace = AgentTrace(
            trace_id=self.trace_id,
            session_id=self.session_id,
            user_query=user_query,
            selected_agent=selected_agent,
            intent=intent,
            risk_level=risk_level,
            entities=entities,
            model_used=model_used,
            latency_ms=latency_ms,
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            approval_required=approval_required,
            approval_id=approval_id,
            handoff_count=handoff_count,
            citations=citations,
            workflow_steps=all_steps,
            status="completed",
            final_answer=final_answer,
        )
        db.add(trace)

        for tc in self.tool_calls:
            db.add(AgentToolCall(
                tool_call_id=f"tc_{uuid.uuid4().hex[:12]}",
                trace_id=self.trace_id,
                agent_name=tc.agent_name,
                tool_name=tc.tool_name,
                tool_input=tc.tool_input,
                tool_output=tc.tool_output,
                latency_ms=tc.latency_ms,
            ))

        for ho in self.handoffs:
            db.add(AgentHandoff(
                handoff_id=f"ho_{uuid.uuid4().hex[:12]}",
                trace_id=self.trace_id,
                from_agent=ho.from_agent,
                to_agent=ho.to_agent,
                reason=ho.reason,
                handoff_payload=ho.payload,
            ))

        db.flush()

        from app.observability.cost_tracker import track_cost

        track_cost(
            agent_name=selected_agent or "unknown",
            model=model_used,
            input_tokens=token_usage,
            output_tokens=0,
            trace_id=self.trace_id,
            task_type="generate",
        )
