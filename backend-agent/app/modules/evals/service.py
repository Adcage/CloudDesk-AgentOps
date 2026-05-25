import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EvalCase, EvalResult
from app.prompts.versions import CURRENT_VERSIONS
from app.schemas.chat import ChatRequest
from app.workflow.graph import execute_workflow

logger = logging.getLogger(__name__)


def _normalize_expected_tools(expected_tools_raw: str | None, expected_doc: str | None) -> list[str]:
    expected_tools = expected_tools_raw.split(",") if expected_tools_raw else []
    normalized = [t.strip() for t in expected_tools if t.strip()]
    if expected_doc and "search_knowledge_base" not in normalized:
        normalized.append("search_knowledge_base")
    return normalized


def _tool_calls_match(actual_tool_calls: list[str], expected_tools: list[str]) -> bool:
    actual = set(actual_tool_calls or [])
    expected = set(expected_tools or [])
    if not expected:
        return True

    substitutes = {
        "get_order_status": {"get_order_status", "get_customer_history"},
    }

    for tool in expected:
        allowed = substitutes.get(tool, {tool})
        if actual.isdisjoint(allowed):
            return False
    return True


def _is_case_successful(
    expected_action: str | None,
    retrieval_hit: bool,
    tool_call_correct: bool,
    approval_routing_correct: bool,
) -> bool:
    if expected_action in {"answer_policy", "answer_troubleshooting"}:
        return retrieval_hit and tool_call_correct
    if expected_action in {"billing_issue", "refund_request", "ticket_create", "close_account", "modify_plan"}:
        return tool_call_correct and approval_routing_correct
    return retrieval_hit or tool_call_correct or approval_routing_correct


class EvalService:
    def __init__(self, db: Session):
        self.db = db

    async def run_evaluation(self, case_ids: list[str] | None = None) -> list[dict]:
        query = select(EvalCase)
        if case_ids:
            query = query.where(EvalCase.case_id.in_(case_ids))
        cases = self.db.execute(query).scalars().all()

        results = []
        for case in cases:
            start_time = time.time()
            trace_id = f"eval_{uuid.uuid4().hex[:12]}"

            chat_request = ChatRequest(
                trace_id=trace_id,
                conversation_id=f"eval_conv_{case.case_id}",
                user_id="eval_runner",
                user_role="admin",
                message=case.question,
            )

            try:
                response = await execute_workflow(chat_request, self.db)

                expected_tools = _normalize_expected_tools(case.expected_tools, case.expected_doc)

                tool_call_names = response.tool_calls
                tool_call_correct = _tool_calls_match(tool_call_names, expected_tools)

                approval_routing_correct = True
                if case.expected_action in {"refund_request", "close_account", "modify_plan"} and case.risk_level == "high":
                    approval_routing_correct = response.approval_required

                latency_ms = int((time.time() - start_time) * 1000)

                retrieval_hit = bool(case.expected_doc and case.expected_doc in (response.citations or []))
                task_success = _is_case_successful(
                    expected_action=case.expected_action,
                    retrieval_hit=retrieval_hit,
                    tool_call_correct=tool_call_correct,
                    approval_routing_correct=approval_routing_correct,
                )

                result_id = f"evr_{uuid.uuid4().hex[:12]}"
                eval_result = EvalResult(
                    result_id=result_id,
                    case_id=case.case_id,
                    trace_id=trace_id,
                    retrieval_hit=retrieval_hit,
                    tool_call_correct=tool_call_correct,
                    approval_routing_correct=approval_routing_correct,
                    task_success=task_success,
                    latency_ms=latency_ms,
                    estimated_cost=0,
                    detail={
                        "prompt_version": result_prompt_version(response.workflow_steps),
                        "question": case.question,
                        "expected_doc": case.expected_doc,
                        "expected_tools": expected_tools,
                        "expected_action": case.expected_action,
                        "actual_agent": response.selected_agent,
                        "actual_citations": response.citations,
                        "actual_tool_calls": response.tool_calls,
                        "actual_approval_required": response.approval_required,
                        "answer_preview": response.answer[:200],
                    },
                )
                self.db.add(eval_result)
                self.db.flush()

                results.append({
                    "result_id": result_id,
                    "case_id": case.case_id,
                    "question": case.question,
                    "retrieval_hit": eval_result.retrieval_hit,
                    "tool_call_correct": eval_result.tool_call_correct,
                    "approval_routing_correct": eval_result.approval_routing_correct,
                    "task_success": eval_result.task_success,
                    "latency_ms": latency_ms,
                    "selected_agent": response.selected_agent,
                })

            except Exception as e:
                logger.error(f"Eval case {case.case_id} failed: {e}")
                results.append({
                    "result_id": f"evr_{uuid.uuid4().hex[:12]}",
                    "case_id": case.case_id,
                    "question": case.question,
                    "error": str(e),
                    "task_success": False,
                })

        self.db.commit()
        return results

    async def list_results(self, page: int = 1, page_size: int = 10) -> dict:
        offset = (page - 1) * page_size
        total = len(self.db.execute(select(EvalResult)).scalars().all())
        rows = self.db.execute(
            select(EvalResult)
            .order_by(EvalResult.created_at.desc())
            .offset(offset)
            .limit(page_size)
        ).scalars().all()

        return {
            "records": [self._serialize_result(row) for row in rows],
            "total": total,
            "current": page,
            "size": page_size,
        }

    async def get_summary(self) -> dict:
        rows = self.db.execute(select(EvalResult)).scalars().all()
        if not rows:
            return {
                "total": 0,
                "pass_rate": 0,
                "retrieval_hit_rate": 0,
                "tool_accuracy": 0,
                "approval_accuracy": 0,
            }

        total = len(rows)
        pass_count = sum(1 for row in rows if row.task_success)
        retrieval_hits = sum(1 for row in rows if row.retrieval_hit)
        tool_hits = sum(1 for row in rows if row.tool_call_correct)
        approval_rows = [row for row in rows if row.approval_routing_correct is not None]
        approval_hits = sum(1 for row in approval_rows if row.approval_routing_correct)

        return {
            "total": total,
            "pass_rate": round(pass_count / total * 100, 1),
            "retrieval_hit_rate": round(retrieval_hits / total * 100, 1),
            "tool_accuracy": round(tool_hits / total * 100, 1),
            "approval_accuracy": round(approval_hits / len(approval_rows) * 100, 1) if approval_rows else 0,
        }

    async def group_by_version(self) -> list[dict]:
        rows = self.db.execute(select(EvalResult)).scalars().all()
        groups: dict[str, dict] = {}
        for row in rows:
            detail = row.detail or {}
            version = detail.get("prompt_version", CURRENT_VERSIONS.get("billing", "v1"))
            bucket = groups.setdefault(version, {"total": 0, "success": 0, "latency": 0, "cost": 0.0})
            bucket["total"] += 1
            bucket["success"] += 1 if row.task_success else 0
            bucket["latency"] += row.latency_ms or 0
            bucket["cost"] += float(row.estimated_cost or 0)

        return [
            {
                "version": version,
                "total": bucket["total"],
                "pass_rate": round(bucket["success"] / bucket["total"] * 100, 1) if bucket["total"] else 0,
                "avg_latency_ms": round(bucket["latency"] / bucket["total"], 1) if bucket["total"] else 0,
                "avg_cost": round(bucket["cost"] / bucket["total"], 6) if bucket["total"] else 0,
            }
            for version, bucket in groups.items()
        ]

    def _serialize_result(self, row: EvalResult) -> dict:
        detail = row.detail or {}
        return {
            "result_id": row.result_id,
            "case_id": row.case_id,
            "trace_id": row.trace_id,
            "retrieval_hit": row.retrieval_hit,
            "tool_call_correct": row.tool_call_correct,
            "approval_routing_correct": row.approval_routing_correct,
            "task_success": row.task_success,
            "latency_ms": row.latency_ms,
            "estimated_cost": float(row.estimated_cost or 0),
            "prompt_version": detail.get("prompt_version", CURRENT_VERSIONS.get("billing", "v1")),
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }


def result_prompt_version(workflow_steps: list[dict]) -> str:
    for step in workflow_steps or []:
        if step.get("agent") == "versioning":
            detail = step.get("detail") or {}
            version = detail.get("prompt_version")
            if version:
                return version
    return CURRENT_VERSIONS.get("billing", "v1")
