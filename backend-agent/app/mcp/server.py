"""CloudDesk MCP Tool Server

将现有 Agent 工具包装为 MCP 协议工具，通过 SSE 协议暴露。
独立运行于 8001 端口，不与 Agent 主流程耦合。

启动方式:
    python -m app.mcp.server --transport sse --port 8001
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("CloudDesk Agent Tool Server", version="1.0.0")


async def _call_tool(func, **kwargs):
    try:
        result = await func(**kwargs)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_customer_profile(customer_id: str) -> dict:
    """查询客户信息：返回客户名称、邮箱、套餐、状态、风险等级。

    Args:
        customer_id: 客户ID，如 C002
    """
    from app.tools.customer_tools import _get_customer_profile

    return await _call_tool(_get_customer_profile, customer_id=customer_id)


@mcp.tool()
async def get_customer_history(customer_id: str) -> dict:
    """查询客户历史记录：返回历史工单数、退款记录、订单数等聚合信息。

    Args:
        customer_id: 客户ID，如 C002
    """
    from app.tools.customer_tools import _get_customer_history

    return await _call_tool(_get_customer_history, customer_id=customer_id)


@mcp.tool()
async def get_order_status(order_id: str) -> dict:
    """查询订单状态：返回订单金额、状态、问题类型。

    Args:
        order_id: 订单ID，如 O1002
    """
    from app.tools.order_tools import _get_order_status

    return await _call_tool(_get_order_status, order_id=order_id)


@mcp.tool()
async def create_ticket(
    customer_id: str,
    subject: str,
    category: str,
    priority: str = "medium",
) -> dict:
    """创建工单。

    Args:
        customer_id: 客户ID
        subject: 工单主题
        category: 工单分类，如 billing/account/technical
        priority: 优先级：low/medium/high
    """
    from app.tools.ticket_tools import _create_ticket

    return await _call_tool(
        _create_ticket,
        customer_id=customer_id,
        subject=subject,
        category=category,
        priority=priority,
    )


@mcp.tool()
async def escalate_ticket(ticket_id: str, reason: str) -> dict:
    """升级工单到更高级别处理。

    Args:
        ticket_id: 工单ID
        reason: 升级原因
    """
    from app.tools.ticket_tools import escalate_ticket as _escalate

    return await _call_tool(_escalate, ticket_id=ticket_id, reason=reason)


@mcp.tool()
async def create_refund_approval(
    customer_id: str,
    order_id: str,
    amount: float,
    reason: str,
) -> dict:
    """创建退款审批单（需主管审批后才执行退款）。

    Args:
        customer_id: 客户ID
        order_id: 订单ID
        amount: 退款金额
        reason: 退款原因
    """
    from app.tools.approval_tools import _create_refund_approval

    return await _call_tool(
        _create_refund_approval,
        customer_id=customer_id,
        order_id=order_id,
        action="refund",
        amount=amount,
        reason=reason,
    )


@mcp.tool()
async def draft_email(customer_id: str, subject: str, context: str) -> dict:
    """生成邮件草稿。

    Args:
        customer_id: 客户ID
        subject: 邮件主题
        context: 邮件内容上下文
    """
    return {
        "customer_id": customer_id,
        "subject": subject,
        "body": f"[草稿] {context}",
        "status": "draft",
    }


if __name__ == "__main__":
    mcp.run(transport="sse", port=8001)
