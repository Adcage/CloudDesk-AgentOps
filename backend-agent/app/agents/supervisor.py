import json
import logging
import re

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.guardrails.injection_defense import detect_injection
from app.memory.customer_memory import get_memory_summary
from app.prompts import load_prompt
from app.routing.model_router import select_model

logger = logging.getLogger(__name__)


def _estimate_complexity(message: str, context: str = "") -> int:
    score = 3
    if len(message or "") > 40:
        score += 2
    if len(message or "") > 80:
        score += 1
    if context:
        score += 1
    if any(token in (message or "") for token in ["审批", "退款", "关闭账号", "修改套餐"]):
        score += 2
    return min(score, 10)


def _extract_entities_by_regex(message: str) -> dict:
    customer_match = re.search(r"C\d{3,}", message, re.IGNORECASE)
    order_match = re.search(r"O\d{3,}", message, re.IGNORECASE)
    amount_match = re.search(r"(?:\$|￥|¥)\s*(\d+(?:\.\d+)?)", message)
    if not amount_match:
        amount_match = re.search(r"退款\s*(\d+(?:\.\d+)?)", message)
    if not amount_match:
        amount_match = re.search(r"(?:金额|多收(?:了)?|收费|费用)\s*(\d+(?:\.\d+)?)", message)

    amount = None
    if amount_match and any(token in message for token in ["退款", "$", "¥", "￥"]):
        amount = float(amount_match.group(1))

    return {
        "customer_id": customer_match.group(0).upper() if customer_match else None,
        "order_id": order_match.group(0).upper() if order_match else None,
        "amount": amount,
    }

INTENT_ENUM = [
    "policy_qa",
    "login_issue",
    "billing_issue",
    "refund_request",
    "ticket_create",
    "email_draft",
    "high_risk_action",
]

INTENT_AGENT_MAP: dict[str, str] = {
    "policy_qa": "billing_agent",
    "billing_issue": "billing_agent",
    "refund_request": "billing_agent",
    "ticket_create": "billing_agent",
    "login_issue": "account_agent",
    "account_issue": "account_agent",
    "email_draft": "billing_agent",
    "high_risk_action": "account_agent",
}

RISK_LEVEL_MAP: dict[str, str] = {
    "high_risk_action": "high",
    "refund_request": "medium",
    "billing_issue": "medium",
    "login_issue": "low",
    "policy_qa": "low",
    "ticket_create": "low",
    "email_draft": "low",
    "account_issue": "medium",
}

INTENT_CLASSIFICATION_PROMPT = """你是一个意图分类器。根据用户消息和对话上下文，判断用户的意图并抽取实体。

意图枚举：{intent_list}

请严格按以下 JSON 格式输出，不要输出其他内容：
{{
    "intent": "意图值",
    "entities": {{
        "customer_id": "客户ID，若未提及则null",
        "order_id": "订单ID，若未提及则null",
        "amount": 退款金额（数字），若未提及则null
    }},
    "risk_level": "high/medium/low",
    "reasoning": "简短推理过程"
}}

用户消息：{message}
对话上下文：{context}"""


class SupervisorAgent:
    def __init__(self):
        self.api_key = settings.openai_api_key or None
        self.base_url = settings.openai_base_url or None
        self.intent_prompt, self.prompt_version = load_prompt("supervisor")

    async def attach_customer_memory(self, result: dict, db: Session) -> dict:
        entities = result.get("entities") or {}
        customer_id = entities.get("customer_id")
        if not customer_id:
            return result

        memory_summary = await get_memory_summary(customer_id, db)
        if not memory_summary:
            return result

        merged_entities = dict(entities)
        merged_entities["customer_memory"] = memory_summary
        return {
            **result,
            "entities": merged_entities,
        }

    def _build_llm(self, task_type: str, complexity: int, risk_level: str, temperature: float = 0):
        return ChatOpenAI(
            model=select_model(task_type, complexity=complexity, risk_level=risk_level),
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=temperature,
        )

    async def classify_intent(
        self,
        message: str,
        context: str = "",
    ) -> dict:
        if detect_injection(message):
            return {
                "intent": "high_risk_action",
                "entities": {},
                "risk_level": "high",
                "selected_agent": "approval_agent",
            }

        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            intent_list=", ".join(INTENT_ENUM),
            message=message,
            context=context or "无",
        )
        prompt = f"{self.intent_prompt}\n\n{prompt}"

        try:
            llm = self._build_llm("intent_classification", _estimate_complexity(message, context), "low")
            response = await llm.ainvoke(prompt)
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"意图分类失败，使用默认策略: {e}")
            result = self._fallback_classify(message)

        intent = result.get("intent", "policy_qa")
        if intent not in INTENT_AGENT_MAP:
            intent = "policy_qa"

        entities = result.get("entities", {})
        regex_entities = _extract_entities_by_regex(message)
        entities = {
            "customer_id": regex_entities.get("customer_id") or entities.get("customer_id"),
            "order_id": regex_entities.get("order_id") or entities.get("order_id"),
            "amount": regex_entities.get("amount") if regex_entities.get("amount") is not None else entities.get("amount"),
        }
        risk_level = result.get("risk_level") or RISK_LEVEL_MAP.get(intent, "low")

        selected_agent = INTENT_AGENT_MAP[intent]

        return {
            "intent": intent,
            "entities": entities,
            "risk_level": risk_level,
            "selected_agent": selected_agent,
            "prompt_version": self.prompt_version,
        }

    def _fallback_classify(self, message: str) -> dict:
        lower = message.lower()
        info_keywords = ["查询", "查看", "状态", "怎么样", "是什么", "如何", "怎么", "多少", "在哪", "有没有"]
        is_info_query = any(w in message for w in info_keywords)
        if any(w in lower for w in ["退款", "refund", "退钱"]):
            intent = "billing_issue" if is_info_query else "refund_request"
            return {"intent": intent, "entities": _extract_entities_by_regex(message), "risk_level": "low" if is_info_query else "medium"}
        if any(w in lower for w in ["账单", "billing", "扣费", "费用"]):
            return {"intent": "billing_issue", "entities": _extract_entities_by_regex(message), "risk_level": "medium"}
        if any(w in lower for w in ["登录", "login", "密码", "password"]):
            return {"intent": "login_issue", "entities": _extract_entities_by_regex(message), "risk_level": "low"}
        if any(w in lower for w in ["关账", "close account", "删除账号"]):
            return {"intent": "high_risk_action", "entities": _extract_entities_by_regex(message), "risk_level": "high"}
        return {"intent": "policy_qa", "entities": _extract_entities_by_regex(message), "risk_level": "low"}

    async def generate_final_answer(
        self,
        query: str,
        intent: str,
        specialist_result: str,
        citations: list[str],
        context: str = "",
    ) -> str:
        risk_level = RISK_LEVEL_MAP.get(intent, "low")
        llm = self._build_llm("final_answer", _estimate_complexity(query, context), risk_level, temperature=0.3)

        citation_text = ""
        if citations:
            citation_text = "\n\n参考来源：\n" + "\n".join(f"- {c}" for c in citations)

        prompt = f"""你是一个专业的客服助手。请根据以下信息，生成对用户问题的最终回复。

用户问题：{query}
意图：{intent}
专家Agent回复：{specialist_result}
对话上下文：{context or '无'}
{citation_text}

请用清晰、专业的中文回复用户。如果有引用来源，请在回复末尾标注。"""

        response = await llm.ainvoke(prompt)
        return response.content.strip()
