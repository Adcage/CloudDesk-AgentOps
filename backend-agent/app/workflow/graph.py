import logging
import uuid
from typing import TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents.account import AccountAgent
from app.agents.approval import ApprovalAgent
from app.agents.billing import BillingAgent
from app.agents.supervisor import SupervisorAgent
from app.core.config import settings
from app.guardrails.fact_check import check_factual_claims
from app.guardrails.injection_defense import detect_injection
from app.guardrails.pii_filter import detect_and_filter_pii
from app.guardrails.tool_policy import validate_tool_access
from app.memory.customer_memory import update_memory_from_session
from app.memory.session_memory import create_or_get_session, load_session, save_message
from app.observability.trace_logger import TraceLogger
from app.routing.model_router import select_model
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

MAX_HANDOFF_COUNT = settings.max_handoff_count


class AgentState(TypedDict, total=False):
    query: str
    session_id: str
    trace_id: str
    intent: str
    entities: dict
    risk_level: str
    selected_agent: str
    retrieved_docs: list[dict]
    tool_call_results: list[dict]
    handoff_count: int
    approval_required: bool
    approval_id: str | None
    final_answer: str
    citations: list[str]
    tool_calls: list[str]
    tool_call_results: list[dict]
    conversation_context: str
    model_used: str
    workflow_steps: list[dict]
    prompt_version: str


def _build_conversation_context(session_data: dict | None) -> str:
    if not session_data or not session_data.get("messages"):
        return ""
    messages = session_data["messages"][-10:]
    parts = [f"{m['role']}: {m['content']}" for m in messages]
    return "\n".join(parts)


def _append_step(state: AgentState, agent: str, action: str, detail: dict | None = None) -> list[dict]:
    steps = list(state.get("workflow_steps", []))
    steps.append({
        "agent": agent,
        "action": action,
        "detail": detail or {},
    })
    return steps


async def load_session_memory_node(state: AgentState) -> dict:
    trace_id = state.get("trace_id", "")
    conversation_id = state.get("session_id", "")

    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        session_id = await create_or_get_session(
            conversation_id=conversation_id or f"conv_{trace_id}",
            user_id="",
            db=db,
        )
        session_data = await load_session(session_id, db)
        context = _build_conversation_context(session_data)
        db.commit()
    except Exception:
        db.rollback()
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        context = ""
    finally:
        db.close()

    steps = _append_step(state, "load_session_memory", "加载会话记忆", {
        "session_id": session_id,
        "has_context": bool(context),
        "context_length": len(context),
    })

    return {
        "session_id": session_id,
        "conversation_context": context,
        "handoff_count": 0,
        "tool_call_results": [],
        "citations": [],
        "tool_calls": [],
        "approval_required": False,
        "approval_id": None,
        "retrieved_docs": [],
        "final_answer": "",
        "risk_level": "low",
        "workflow_steps": steps,
    }


async def run_supervisor(state: AgentState) -> dict:
    injection_detected = detect_injection(state.get("query", ""))

    if injection_detected:
        steps = _append_step(state, "supervisor_agent", "注入检测命中，直接路由审批", {
            "query": state.get("query", "")[:200],
            "injection_detected": True,
        })
        return {
            "intent": "high_risk_action",
            "entities": {},
            "risk_level": "high",
            "selected_agent": "approval_agent",
            "workflow_steps": steps,
        }

    supervisor = SupervisorAgent()
    result = await supervisor.classify_intent(
        message=state["query"],
        context=state.get("conversation_context", ""),
    )
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        result = await supervisor.attach_customer_memory(result, db)
    finally:
        db.close()

    steps = _append_step(state, "supervisor_agent", "意图分类完成", {
        "intent": result["intent"],
        "entities": result.get("entities", {}),
        "risk_level": result.get("risk_level", "low"),
        "selected_agent": result["selected_agent"],
        "model": select_model("intent_classification"),
        "prompt_version": result.get("prompt_version", getattr(supervisor, "prompt_version", "v1")),
    })

    return {
        "intent": result["intent"],
        "entities": result.get("entities", {}),
        "risk_level": result.get("risk_level", "low"),
        "selected_agent": result["selected_agent"],
        "prompt_version": result.get("prompt_version", getattr(supervisor, "prompt_version", "v1")),
        "workflow_steps": steps,
    }


async def run_billing(state: AgentState) -> dict:
    agent = BillingAgent()
    result = await agent.run(
        query=state["query"],
        entities=state.get("entities", {}),
        trace_id=state.get("trace_id", ""),
        context=state.get("conversation_context", ""),
    )

    new_handoff_count = state.get("handoff_count", 0)
    handoff_to = result.get("handoff_to")
    if handoff_to and new_handoff_count < MAX_HANDOFF_COUNT:
        new_handoff_count += 1

    steps = _append_step(state, "billing_agent", "账单处理完成", {
        "approval_required": result.get("approval_required", False),
        "handoff_to": handoff_to,
        "handoff_count": new_handoff_count,
        "tool_count": len(result.get("tool_call_results", [])),
        "citation_count": len(result.get("citations", [])),
    })

    return {
        "final_answer": result["answer"],
        "citations": result.get("citations", []),
        "tool_call_results": state.get("tool_call_results", []) + result.get("tool_call_results", []),
        "tool_calls": state.get("tool_calls", []) + [r["tool"] for r in result.get("tool_call_results", [])],
        "approval_required": result.get("approval_required", False),
        "approval_id": result.get("approval_id"),
        "handoff_count": new_handoff_count,
        "selected_agent": handoff_to if handoff_to else state.get("selected_agent", "billing_agent"),
        "prompt_version": result.get("prompt_version", state.get("prompt_version", "v1")),
        "workflow_steps": steps,
    }


async def run_account(state: AgentState) -> dict:
    agent = AccountAgent()
    result = await agent.run(
        query=state["query"],
        entities=state.get("entities", {}),
        trace_id=state.get("trace_id", ""),
        context=state.get("conversation_context", ""),
    )

    new_handoff_count = state.get("handoff_count", 0)
    handoff_to = result.get("handoff_to")
    if handoff_to and new_handoff_count < MAX_HANDOFF_COUNT:
        new_handoff_count += 1

    steps = _append_step(state, "account_agent", "账号处理完成", {
        "approval_required": result.get("approval_required", False),
        "handoff_to": handoff_to,
        "handoff_count": new_handoff_count,
        "tool_count": len(result.get("tool_call_results", [])),
        "citation_count": len(result.get("citations", [])),
    })

    return {
        "final_answer": result["answer"],
        "citations": result.get("citations", []),
        "tool_call_results": state.get("tool_call_results", []) + result.get("tool_call_results", []),
        "tool_calls": state.get("tool_calls", []) + [r["tool"] for r in result.get("tool_call_results", [])],
        "approval_required": result.get("approval_required", False),
        "approval_id": result.get("approval_id"),
        "handoff_count": new_handoff_count,
        "selected_agent": handoff_to if handoff_to else state.get("selected_agent", "account_agent"),
        "prompt_version": result.get("prompt_version", state.get("prompt_version", "v1")),
        "workflow_steps": steps,
    }


async def run_approval(state: AgentState) -> dict:
    agent = ApprovalAgent()
    result = await agent.run(
        query=state["query"],
        entities=state.get("entities", {}),
        trace_id=state.get("trace_id", ""),
        context=state.get("conversation_context", ""),
        action=state.get("intent", "refund"),
        amount=state.get("entities", {}).get("amount"),
    )

    steps = _append_step(state, "approval_agent", "审批处理完成", {
        "approval_required": result.get("approval_required", False),
        "approval_id": result.get("approval_id"),
        "action": state.get("intent", "refund"),
        "amount": state.get("entities", {}).get("amount"),
    })

    return {
        "final_answer": result["answer"],
        "citations": state.get("citations", []) + result.get("citations", []),
        "tool_call_results": state.get("tool_call_results", []) + result.get("tool_call_results", []),
        "tool_calls": state.get("tool_calls", []) + [r["tool"] for r in result.get("tool_call_results", [])],
        "approval_required": result.get("approval_required", False),
        "approval_id": result.get("approval_id"),
        "selected_agent": "approval_agent",
        "prompt_version": result.get("prompt_version", state.get("prompt_version", "v1")),
        "workflow_steps": steps,
    }


async def check_guardrails(state: AgentState) -> dict:
    handoff_count = state.get("handoff_count", 0)
    approval_required = state.get("approval_required", False)
    over_limit = handoff_count > MAX_HANDOFF_COUNT

    steps = _append_step(state, "check_guardrails", "守卫检查", {
        "handoff_count": handoff_count,
        "max_handoff": MAX_HANDOFF_COUNT,
        "over_limit": over_limit,
        "approval_required": approval_required,
        "approval_id": state.get("approval_id"),
        "need_approval_route": approval_required and not over_limit and not state.get("approval_id"),
    })

    if over_limit:
        return {
            "final_answer": state.get("final_answer", "") + "\n\n（已达到最大转交次数限制，请创建人工工单获取进一步帮助。）",
            "approval_required": False,
            "tool_calls": state.get("tool_calls", []),
            "workflow_steps": steps,
        }

    return {
        "tool_calls": state.get("tool_calls", []),
        "workflow_steps": steps,
    }


async def generate_final_answer(state: AgentState) -> dict:
    if state.get("final_answer") and not state.get("approval_required"):
        answer = state["final_answer"]
    elif state.get("approval_required"):
        answer = state.get("final_answer", "此操作需要审批。")
    else:
        supervisor = SupervisorAgent()
        answer = await supervisor.generate_final_answer(
            query=state["query"],
            intent=state.get("intent", "policy_qa"),
            specialist_result=state.get("final_answer", ""),
            citations=state.get("citations", []),
            context=state.get("conversation_context", ""),
        )

    fact_ok, fact_violations = check_factual_claims(answer)
    filtered_answer, pii_detections = detect_and_filter_pii(answer)
    answer = filtered_answer

    model_used = select_model("final_answer")
    steps = _append_step(state, "generate_final_answer", "生成最终回复", {
        "model": model_used,
        "answer_length": len(answer),
        "approval_required": state.get("approval_required", False),
        "approval_id": state.get("approval_id"),
        "intent": state.get("intent"),
        "selected_agent": state.get("selected_agent"),
        "fact_check_passed": fact_ok,
        "fact_check_violations": fact_violations,
        "pii_detection_count": len(pii_detections),
        "prompt_version": state.get("prompt_version", "v1"),
    })

    return {
        "final_answer": answer,
        "model_used": model_used,
        "prompt_version": state.get("prompt_version", "v1"),
        "workflow_steps": steps,
    }


async def save_trace_node(state: AgentState) -> dict:
    trace_logger = TraceLogger(
        trace_id=state.get("trace_id", f"TR_{uuid.uuid4().hex[:12]}"),
        session_id=state.get("session_id", ""),
    )

    if state.get("approval_required") and state.get("selected_agent"):
        prev_agent = "supervisor_agent"
        for step in reversed(state.get("workflow_steps", [])):
            if step.get("agent") not in ("supervisor_agent", "check_guardrails", "generate_final_answer", "load_session_memory"):
                if step.get("agent") != "approval_agent":
                    prev_agent = step["agent"]
                    break
        trace_logger.log_handoff(
            from_agent=prev_agent,
            to_agent="approval_agent",
            reason=f"审批需要: intent={state.get('intent')}, risk_level={state.get('risk_level')}",
            payload={
                "approval_required": state.get("approval_required"),
                "approval_id": state.get("approval_id"),
                "intent": state.get("intent"),
                "entities": state.get("entities"),
            },
        )

    for tool_result in state.get("tool_call_results", []):
        trace_logger.log_tool_call(
            agent_name=state.get("selected_agent", "unknown"),
            tool_name=tool_result.get("tool", "unknown"),
            tool_input=tool_result.get("input", {}),
            tool_output=tool_result.get("output", {}),
            latency_ms=0,
        )

    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        await trace_logger.save(
            db=db,
            final_answer=state.get("final_answer", ""),
            model_used=state.get("model_used", select_model("final_answer")),
            token_usage=0,
            intent=state.get("intent"),
            user_query=state.get("query"),
            risk_level=state.get("risk_level"),
            entities=state.get("entities"),
            approval_required=state.get("approval_required", False),
            approval_id=state.get("approval_id"),
            handoff_count=state.get("handoff_count", 0),
            citations=state.get("citations", []),
            workflow_steps=state.get("workflow_steps", []),
            prompt_version=state.get("prompt_version", "v1"),
            selected_agent=state.get("selected_agent"),
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"保存 trace 失败: {e}")
    finally:
        db.close()

    return {}


def route_to_specialist(state: AgentState) -> str:
    selected_agent = state.get("selected_agent", "billing_agent")
    if selected_agent in ("billing_agent", "account_agent", "approval_agent"):
        return selected_agent
    return "billing_agent"


def need_approval(state: AgentState) -> str:
    if state.get("approval_required") and state.get("handoff_count", 0) < MAX_HANDOFF_COUNT:
        approval_already_created = bool(state.get("approval_id")) or "create_refund_approval" in state.get("tool_calls", [])
        if not approval_already_created:
            return "approval_agent"
    return "generate_final_answer"


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("load_session_memory", load_session_memory_node)
    workflow.add_node("supervisor_agent", run_supervisor)
    workflow.add_node("billing_agent", run_billing)
    workflow.add_node("account_agent", run_account)
    workflow.add_node("approval_agent", run_approval)
    workflow.add_node("check_guardrails", check_guardrails)
    workflow.add_node("generate_final_answer", generate_final_answer)
    workflow.add_node("save_trace", save_trace_node)

    workflow.set_entry_point("load_session_memory")
    workflow.add_edge("load_session_memory", "supervisor_agent")
    workflow.add_conditional_edges(
        "supervisor_agent",
        route_to_specialist,
        {
            "billing_agent": "billing_agent",
            "account_agent": "account_agent",
            "approval_agent": "approval_agent",
        },
    )
    workflow.add_edge("billing_agent", "check_guardrails")
    workflow.add_edge("account_agent", "check_guardrails")
    workflow.add_edge("approval_agent", "check_guardrails")
    workflow.add_conditional_edges(
        "check_guardrails",
        need_approval,
        {
            "approval_agent": "approval_agent",
            "generate_final_answer": "generate_final_answer",
        },
    )
    workflow.add_edge("generate_final_answer", "save_trace")
    workflow.add_edge("save_trace", END)

    return workflow.compile()


graph_app = build_graph()


async def execute_workflow(request: ChatRequest, db: Session) -> ChatResponse:
    trace_logger = TraceLogger(
        trace_id=request.trace_id,
        session_id=request.conversation_id,
    )

    initial_state: AgentState = {
        "query": request.message,
        "session_id": request.conversation_id,
        "trace_id": request.trace_id,
        "intent": "",
        "entities": {},
        "risk_level": "low",
        "selected_agent": "",
        "retrieved_docs": [],
        "tool_call_results": [],
        "handoff_count": 0,
        "approval_required": False,
        "approval_id": None,
        "final_answer": "",
        "citations": [],
        "tool_calls": [],
        "model_used": "",
        "workflow_steps": [],
    }

    try:
        result = await graph_app.ainvoke(initial_state)

        answer = result.get("final_answer", "")
        session_id = result.get("session_id", request.conversation_id)

        await save_message(
            session_id=session_id,
            role="user",
            content=request.message,
            trace_id=request.trace_id,
            db=db,
        )
        await save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            trace_id=request.trace_id,
            db=db,
        )
        customer_id = (result.get("entities") or {}).get("customer_id")
        if customer_id:
            await update_memory_from_session(
                customer_id=customer_id,
                session_id=session_id,
                final_answer=answer,
                db=db,
            )
        db.commit()

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        trace_logger.log_step("workflow", "error", {"error": str(e)})
        answer = f"处理请求时发生错误: {str(e)}"
        result = {
            "selected_agent": "error",
            "citations": [],
            "tool_calls": [],
            "approval_required": False,
            "approval_id": None,
            "intent": "",
            "risk_level": "low",
            "entities": {},
            "workflow_steps": [],
        }

    tool_call_results = result.get("tool_call_results", [])
    citation_details = _extract_citation_details(tool_call_results)
    customer_context = _extract_customer_context(tool_call_results)
    order_context = _extract_order_context(tool_call_results)

    return ChatResponse(
        conversation_id=session_id if 'session_id' in locals() else request.conversation_id,
        answer=answer,
        selected_agent=result.get("selected_agent", ""),
        citations=result.get("citations", []),
        tool_calls=result.get("tool_calls", []),
        tool_call_results=tool_call_results,
        citation_details=citation_details,
        approval_required=result.get("approval_required", False),
        approval_id=result.get("approval_id"),
        trace_id=request.trace_id,
        customer_context=customer_context,
        order_context=order_context,
        intent=result.get("intent", ""),
        risk_level=result.get("risk_level", "low"),
        entities=result.get("entities", {}),
        workflow_steps=result.get("workflow_steps", []),
    )


def _extract_citation_details(tool_call_results: list[dict]) -> list[dict[str, str]]:
    for item in tool_call_results:
        if item.get("tool") == "search_knowledge_base" and isinstance(item.get("output"), dict):
            docs = item["output"].get("documents", [])
            if isinstance(docs, list):
                return [
                    {"source": d.get("source", ""), "text": d.get("text", "")}
                    for d in docs if isinstance(d, dict) and d.get("source")
                ]
    return []


def _extract_customer_context(tool_call_results: list[dict]) -> dict | None:
    for item in tool_call_results:
        if item.get("tool") == "get_customer_profile" and isinstance(item.get("output"), dict):
            output = item["output"]
            data = output.get("data", output) if isinstance(output, dict) else {}
            if isinstance(data, dict):
                return {
                    "customer_id": data.get("customerId") or data.get("customer_id") or "",
                    "customer_name": data.get("name") or data.get("customerName") or "",
                    "plan": data.get("plan") or "",
                    "risk_level": data.get("riskLevel") or data.get("risk_level") or "low",
                }
    for item in tool_call_results:
        if item.get("tool") == "get_order_status" and isinstance(item.get("output"), dict):
            output = item["output"]
            data = output.get("data", output) if isinstance(output, dict) else {}
            if isinstance(data, dict) and (data.get("customerId") or data.get("customer_id")):
                return {
                    "customer_id": data.get("customerId") or data.get("customer_id") or "",
                    "customer_name": "",
                    "plan": "",
                    "risk_level": "low",
                }
    return None


def _extract_order_context(tool_call_results: list[dict]) -> dict | None:
    for item in tool_call_results:
        if item.get("tool") == "get_order_status" and isinstance(item.get("output"), dict):
            output = item["output"]
            data = output.get("data", output) if isinstance(output, dict) else {}
            if isinstance(data, dict):
                return {
                    "order_id": data.get("orderId") or data.get("order_id") or "",
                    "amount": data.get("amount") or 0,
                    "status": data.get("status") or "",
                }
    return None
