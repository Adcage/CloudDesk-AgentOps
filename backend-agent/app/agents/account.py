import logging

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.guardrails.approval_policy import check_approval_required
from app.prompts import load_prompt
from app.guardrails.tool_policy import validate_tool_access, validate_tool_input
from app.rag.retriever import retrieve
from app.routing.model_router import select_model
from app.tools.customer_tools import _get_customer_profile
from app.tools.ticket_tools import _create_ticket

logger = logging.getLogger(__name__)


def _append_validation_failure(tool_call_results: list[dict], tool_name: str, tool_input: dict, error: str) -> None:
    tool_call_results.append({
        "tool": tool_name,
        "input": tool_input,
        "output": {"error": error},
        "status": "validation_failed",
    })


def _estimate_complexity(query: str, tool_count: int, has_docs: bool, risk_level: str) -> int:
    score = 3
    if len(query or "") > 40:
        score += 1
    if tool_count >= 1:
        score += 1
    if has_docs:
        score += 1
    if risk_level == "high":
        score += 2
    elif risk_level == "medium":
        score += 1
    return min(score, 10)

ACCOUNT_SYSTEM_PROMPT = """你是 CloudDesk 账号与登录专家 Agent。你的职责是：
1. 根据用户问题检索相关文档（登录问题排查、账号安全等）
2. 生成明确的解决步骤
3. 如涉及套餐修改或关闭账号，标记需要审批
4. 否则创建工单或直接给出解决步骤

请根据检索到的文档和工具调用结果，给出专业准确的回复。
如果检索不到相关文档，不要编造内容，建议创建人工工单。"""


class AccountAgent:
    def __init__(self):
        self.api_key = settings.openai_api_key or None
        self.base_url = settings.openai_base_url or None
        self.system_prompt, self.prompt_version = load_prompt("account")

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
        risk_level = entities.get("risk_level", "low")
        customer_memory = entities.get("customer_memory", "")

        if customer_id:
            if not validate_tool_access("account_agent", "get_customer_profile"):
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

        lower_query = query.lower()
        approval_decision = None
        if any(w in lower_query for w in ["修改套餐", "change plan", "升级套餐", "降级套餐"]):
            approval_decision = check_approval_required("modify_plan", 0, risk_level)
        elif any(w in lower_query for w in ["关闭账号", "close account", "删除账号"]):
            approval_decision = check_approval_required("close_account", 0, risk_level)

        if approval_decision and approval_decision.required:
            return {
                "answer": "此操作需要审批（涉及套餐修改或账号关闭）。正在转交审批 Agent 处理。",
                "citations": citations,
                "tool_call_results": tool_call_results,
                "approval_required": True,
                "approval_id": None,
                "handoff_to": "approval_agent",
                "approval_level": approval_decision.level,
            }

        prompt = f"""{self.system_prompt}

用户问题：{query}
对话上下文：{context or '无'}
客户长期记忆：{customer_memory or '无'}
检索到的文档：
{doc_context or '（无相关文档）'}

工具调用结果：
{self._format_tool_results(tool_call_results)}

请生成专业回复："""

        if not doc_context:
            answer = "抱歉，未能找到相关文档。建议为您创建人工工单，由客服专员处理。"
            ticket_input = {
                "customer_id": customer_id or "unknown",
                "subject": query[:200],
                "category": "account",
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
