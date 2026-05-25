import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EvalCase, EvalResult
from app.observability.cost_tracker import estimate_cost
from app.routing.model_router import select_model
from app.schemas.chat import ChatRequest
from app.workflow.graph import execute_workflow

logger = logging.getLogger(__name__)


async def run_evaluation(db: Session) -> list[dict]:
    cases = db.execute(select(EvalCase)).scalars().all()

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
            response = await execute_workflow(chat_request, db)

            expected_tools = (
                [t.strip() for t in case.expected_tools.split(",") if t.strip()]
                if case.expected_tools
                else []
            )

            tool_call_names = response.tool_calls
            tool_call_correct = (
                bool(expected_tools)
                and all(t in tool_call_names for t in expected_tools)
            )

            approval_routing_correct = True
            if case.expected_action == "approval_needed":
                approval_routing_correct = response.approval_required

            retrieval_hit = bool(response.citations)
            expected_doc_hit = (
                case.expected_doc in response.citations
                if case.expected_doc and response.citations
                else False
            )

            task_success = tool_call_correct and (
                retrieval_hit or not case.expected_doc
            )

            latency_ms = int((time.time() - start_time) * 1000)
            model_used = select_model("intent_classification")
            estimated_cost = estimate_cost(model_used, 500, 200)

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
                estimated_cost=estimated_cost,
                detail={
                    "question": case.question,
                    "expected_doc": case.expected_doc,
                    "expected_tools": expected_tools,
                    "expected_action": case.expected_action,
                    "actual_agent": response.selected_agent,
                    "actual_answer_preview": response.answer[:500],
                    "actual_citations": response.citations,
                    "actual_tool_calls": response.tool_calls,
                    "actual_approval_required": response.approval_required,
                    "expected_doc_hit": expected_doc_hit,
                },
            )
            db.add(eval_result)
            db.flush()

            results.append({
                "result_id": result_id,
                "case_id": case.case_id,
                "question": case.question,
                "intent": case.expected_action,
                "risk_level": case.risk_level,
                "selected_agent": response.selected_agent,
                "retrieval_hit": retrieval_hit,
                "expected_doc_hit": expected_doc_hit,
                "tool_call_correct": tool_call_correct,
                "approval_routing_correct": approval_routing_correct,
                "task_success": task_success,
                "latency_ms": latency_ms,
                "estimated_cost": estimated_cost,
            })

        except Exception as e:
            logger.error(f"Eval case {case.case_id} failed: {e}")
            latency_ms = int((time.time() - start_time) * 1000)

            result_id = f"evr_{uuid.uuid4().hex[:12]}"
            eval_result = EvalResult(
                result_id=result_id,
                case_id=case.case_id,
                trace_id=trace_id,
                retrieval_hit=False,
                tool_call_correct=False,
                approval_routing_correct=False,
                task_success=False,
                latency_ms=latency_ms,
                estimated_cost=0,
                detail={
                    "question": case.question,
                    "expected_doc": case.expected_doc,
                    "expected_action": case.expected_action,
                    "error": str(e),
                },
            )
            db.add(eval_result)
            db.flush()

            results.append({
                "result_id": result_id,
                "case_id": case.case_id,
                "question": case.question,
                "intent": case.expected_action,
                "risk_level": case.risk_level,
                "selected_agent": "error",
                "retrieval_hit": False,
                "expected_doc_hit": False,
                "tool_call_correct": False,
                "approval_routing_correct": False,
                "task_success": False,
                "latency_ms": latency_ms,
                "estimated_cost": 0,
                "error": str(e),
            })

    db.commit()
    return results