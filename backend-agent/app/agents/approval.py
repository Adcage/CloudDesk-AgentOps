import logging

from app.guardrails.approval_policy import check_approval_required
from app.guardrails.tool_policy import validate_tool_input
from app.tools.approval_tools import _create_refund_approval

logger = logging.getLogger(__name__)


def _normalize_action(action: str) -> str:
    if action == "refund_request":
        return "refund"
    if action == "high_risk_action":
        return "close_account"
    return action


def _extract_approval_id(approval_result: dict) -> str:
    if not isinstance(approval_result, dict):
        return ""
    if isinstance(approval_result.get("data"), dict):
        data = approval_result["data"]
        return data.get("approvalId") or data.get("approval_id") or ""
    return approval_result.get("approval_id", "")


class ApprovalAgent:
    def __init__(self):
        self.prompt_version = "v1"

    async def run(
        self,
        query: str,
        entities: dict,
        trace_id: str,
        context: str = "",
        action: str = "refund",
        amount: float | None = None,
    ) -> dict:
        normalized_action = _normalize_action(action)
        risk_level = entities.get("risk_level", "low") if entities else "low"
        decision = check_approval_required(normalized_action, amount, risk_level)

        if not decision.required:
            return {
                "answer": "经评估，此操作不需要审批，可以直接执行。",
                "citations": [],
                "tool_call_results": [],
                "approval_required": False,
                "approval_id": None,
                "handoff_to": None,
                "prompt_version": self.prompt_version,
            }

        customer_id = entities.get("customer_id")
        order_id = entities.get("order_id")

        if not customer_id or not order_id:
            return {
                "answer": "此操作需要审批，但缺少客户ID或订单ID。建议提供完整信息后重新提交。",
                "citations": [],
                "tool_call_results": [],
                "approval_required": True,
                "approval_id": None,
                "handoff_to": None,
                "prompt_version": self.prompt_version,
            }

        try:
            approval_input = {
                "customer_id": customer_id,
                "order_id": order_id,
                "action": normalized_action,
                "amount": amount or 0,
                "reason": query,
                "trace_id": trace_id,
            }
            valid, error, cleaned_input = validate_tool_input("create_refund_approval", approval_input)
            if not valid:
                return {
                    "answer": "审批参数校验失败，请联系人工客服处理。",
                    "citations": [],
                    "tool_call_results": [{
                        "tool": "create_refund_approval",
                        "input": approval_input,
                        "output": {"error": error},
                        "status": "validation_failed",
                    }],
                    "approval_required": True,
                    "approval_id": None,
                    "handoff_to": None,
                    "prompt_version": self.prompt_version,
                }

            approval_result = await _create_refund_approval(
                **cleaned_input,
            )

            approval_id = _extract_approval_id(approval_result)
            return {
                "answer": f"此操作需要审批。已创建审批单 {approval_id}，等待主管审批。审批通过后将自动执行。",
                "citations": [],
                "tool_call_results": [{
                    "tool": "create_refund_approval",
                    "input": {
                        **cleaned_input,
                    },
                    "output": approval_result,
                }],
                "approval_required": True,
                "approval_id": approval_id,
                "handoff_to": None,
                "approval_level": decision.level,
                "prompt_version": self.prompt_version,
            }
        except Exception as e:
            logger.error(f"创建审批单失败: {e}")
            return {
                "answer": f"审批流程启动失败：{str(e)}。请联系人工客服处理。",
                "citations": [],
                "tool_call_results": [],
                "approval_required": True,
                "approval_id": None,
                "handoff_to": None,
                "prompt_version": self.prompt_version,
            }
