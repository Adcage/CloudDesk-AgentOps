import logging

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.guardrails.approval_policy import check_approval_required
from app.prompts import load_prompt
from app.guardrails.tool_policy import validate_tool_access, validate_tool_input
from app.rag.retriever import retrieve
from app.routing.model_router import select_model
from app.tools.customer_tools import _get_customer_profile, _get_customer_history
from app.tools.order_tools import _get_order_status
from app.tools.ticket_tools import _create_ticket
from app.tools.approval_tools import _create_refund_approval

logger = logging.getLogger(__name__)


def _append_validation_failure(tool_call_results: list[dict], tool_name: str, tool_input: dict, error: str) -> None:
    tool_call_results.append({
        "tool": tool_name,
        "input": tool_input,
        "output": {"error": error},
        "status": "validation_failed",
    })


def _estimate_complexity(query: str, tool_count: int, has_docs: bool, risk_level: str) -> int:
    score = 4
    if len(query or "") > 50:
        score += 1
    if tool_count >= 2:
        score += 2
    if has_docs:
        score += 1
    if risk_level == "high":
        score += 2
    elif risk_level == "medium":
        score += 1
    return min(score, 10)

BILLING_SYSTEM_PROMPT = """你是 CloudDesk 账单与退款专家 Agent。你的职责是：
1. 根据用户问题检索相关政策文档
2. 调用工具查询客户信息和订单状态
3. 判断是否需要审批（退款 >= $100 或高风险操作）
4. 如需审批，返回 approval_required=True 并说明原因
5. 如不需审批，生成工单或直接回答

请根据检索到的政策文档和工具调用结果，给出专业准确的回复。
如果检索不到相关文档，不要编造内容，建议创建人工工单。"""


class BillingAgent:
    def __init__(self):
        self.api_key = settings.openai_api_key or None
        self.base_url = settings.openai_base_url or None
        self.system_prompt, self.prompt_version = load_prompt("billing")

    async def run(
        self,
        query: str,
        entities: dict,
        trace_id: str,
        context: str = "",
    ) -> dict:
        retrieved_docs = await retrieve(query)
        citations = [doc["source"] for doc in retrieved_docs if doc.get("source")]
        doc_context = "\n\n".join(doc["text"] for doc in retrieved_docs)

        tool_call_results = []
        if retrieved_docs:
            tool_call_results.append({
                "tool": "search_knowledge_base",
                "input": {"query": query},
                "output": {"sources": citations, "count": len(retrieved_docs), "documents": retrieved_docs},
            })
        customer_id = entities.get("customer_id")
        order_id = entities.get("order_id")
        customer_memory = entities.get("customer_memory", "")

        if customer_id:
            if not validate_tool_access("billing_agent", "get_customer_profile"):
                _append_validation_failure(tool_call_results, "get_customer_profile", {"customer_id": customer_id}, "tool_access_denied")
            else:
                valid, error, cleaned_input = validate_tool_input("get_customer_profile", {"customer_id": customer_id})
                if not valid:
                    _append_validation_failure(tool_call_results, "get_customer_profile", {"customer_id": customer_id}, error or "invalid_input")
                else:
                    try:
                        profile = await _get_customer_profile(cleaned_input["customer_id"])
                        tool_call_results.append({
                            "tool": "get_customer_profile",
                            "input": cleaned_input,
                            "output": profile,
                        })
                    except Exception as e:
                        logger.warning(f"获取客户档案失败: {e}")
        
        if customer_id and not order_id:
            valid, error, cleaned_input = validate_tool_input("get_customer_history", {"customer_id": customer_id})
            if not valid:
                _append_validation_failure(tool_call_results, "get_customer_history", {"customer_id": customer_id}, error or "invalid_input")
            else:
                try:
                    history = await _get_customer_history(cleaned_input["customer_id"])
                    tool_call_results.append({
                        "tool": "get_customer_history",
                        "input": cleaned_input,
                        "output": history,
                    })
                    orders = history.get("orders", [])
                    if orders:
                        order_id = orders[0].get("order_id")
                except Exception as e:
                    logger.warning(f"获取客户历史失败: {e}")

        if order_id:
            valid, error, cleaned_input = validate_tool_input("get_order_status", {"order_id": order_id})
            if not valid:
                _append_validation_failure(tool_call_results, "get_order_status", {"order_id": order_id}, error or "invalid_input")
            else:
                try:
                    order = await _get_order_status(cleaned_input["order_id"])
                    tool_call_results.append({
                        "tool": "get_order_status",
                        "input": cleaned_input,
                        "output": order,
                    })
                except Exception as e:
                    logger.warning(f"获取订单状态失败: {e}")

        intent = "billing_issue"
        amount = entities.get("amount")
        risk_level = entities.get("risk_level", "low")
        if amount is not None:
            intent = "refund"
        elif "退款" in query or "refund" in query.lower():
            intent = "refund"

        approval_decision = check_approval_required(intent, amount, risk_level)

        if approval_decision.required:
            return {
                "answer": "此操作需要审批，正在转交审批 Agent 创建审批单。",
                "citations": citations,
                "tool_call_results": tool_call_results,
                "approval_required": True,
                "approval_id": None,
                "handoff_to": "approval_agent",
                "approval_level": approval_decision.level,
            }

        lower_query = query.lower()
        should_create_ticket = any(
            token in query for token in ["创建工单", "我要退款", "申请退款", "帮我退款", "无法访问", "系统异常", "升级处理"]
        )

        if should_create_ticket:
            ticket_input = {
                "customer_id": customer_id or "unknown",
                "subject": query[:200],
                "category": "billing" if intent == "refund" or "账单" in query or "扣费" in query else "support",
                "priority": "high" if intent == "refund" else "medium",
                "agent_summary": f"AI根据当前问题创建工单。问题: {query}",
                "trace_id": trace_id,
            }
            valid, error, cleaned_input = validate_tool_input("create_ticket", ticket_input)
            if not valid:
                _append_validation_failure(tool_call_results, "create_ticket", ticket_input, error or "invalid_input")
                return {
                    "answer": "当前问题本应创建工单，但工单参数校验失败，请联系人工客服处理。",
                    "citations": citations,
                    "tool_call_results": tool_call_results,
                    "approval_required": False,
                    "approval_id": None,
                    "handoff_to": None,
                }
            try:
                ticket_result = await _create_ticket(
                    **cleaned_input,
                )
                tool_call_results.append({
                    "tool": "create_ticket",
                    "input": cleaned_input,
                    "output": ticket_result,
                })
                return {
                    "answer": f"已根据当前问题创建工单 {ticket_result.get('ticket_id', '')}，后续将由人工团队继续处理。",
                    "citations": citations,
                    "tool_call_results": tool_call_results,
                    "approval_required": False,
                    "approval_id": None,
                    "handoff_to": None,
                }
            except Exception as e:
                logger.warning(f"创建工单失败: {e}")

        prompt = f"""{self.system_prompt}

用户问题：{query}
对话上下文：{context or '无'}
客户长期记忆：{customer_memory or '无'}
检索到的政策文档：
{doc_context or '（无相关文档）'}

工具调用结果：
{self._format_tool_results(tool_call_results)}

请生成专业回复："""

        if not doc_context and not tool_call_results:
            answer = "抱歉，未能找到相关政策文档，也无法查询到相关信息。建议为您创建人工工单，由客服专员处理。"
            ticket_input = {
                "customer_id": customer_id or "unknown",
                "subject": query[:200],
                "category": "billing",
                "priority": "medium",
                "agent_summary": f"AI无法自动处理，需要人工介入。问题: {query}",
                "trace_id": trace_id,
            }
            valid, error, cleaned_input = validate_tool_input("create_ticket", ticket_input)
            if not valid:
                _append_validation_failure(tool_call_results, "create_ticket", ticket_input, error or "invalid_input")
                return {
                    "answer": answer + "\n\n工单参数校验失败，请联系人工客服。",
                    "citations": citations,
                    "tool_call_results": tool_call_results,
                    "approval_required": False,
                    "approval_id": None,
                    "handoff_to": None,
                }
            try:
                ticket_result = await _create_ticket(
                    **cleaned_input,
                )
                tool_call_results.append({
                    "tool": "create_ticket",
                    "input": cleaned_input,
                    "output": ticket_result,
                })
                answer += f"\n\n已创建工单：{ticket_result.get('ticket_id', '')}"
            except Exception:
                answer += "\n\n创建工单失败，请联系人工客服。"
            return {
                "answer": answer,
                "citations": citations,
                "tool_call_results": tool_call_results,
                "approval_required": False,
                "approval_id": None,
                "handoff_to": None,
            }

        llm = ChatOpenAI(
            model=select_model(
                "policy_qa",
                complexity=_estimate_complexity(query, len(tool_call_results), bool(doc_context), risk_level),
                risk_level=risk_level,
            ),
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,
        )
        response = await llm.ainvoke(prompt)
        answer = response.content.strip()

        return {
            "answer": answer,
            "citations": citations,
            "tool_call_results": tool_call_results,
            "approval_required": False,
            "approval_id": None,
            "handoff_to": None,
            "prompt_version": self.prompt_version,
        }

    def _format_tool_results(self, results: list[dict]) -> str:
        if not results:
            return "（无）"
        parts = []
        for r in results:
            parts.append(f"- {r['tool']}({r['input']}): {r['output']}")
        return "\n".join(parts)
