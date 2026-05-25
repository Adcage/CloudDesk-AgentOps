"""模块注册系统。

模块启用列表通过代码常量维护，不从环境变量读取。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


@dataclass(frozen=True)
class ModuleSpec:
    """模块规格定义"""

    router_path: str  # 路由模块路径 "app.modules.health.router"
    prefix: str = ""  # URL 前缀
    tags: tuple[str, ...] = ()  # OpenAPI 标签
    requires: tuple[str, ...] = ()  # 依赖的其他模块


# 模块注册表
MODULE_REGISTRY: dict[str, ModuleSpec] = {
    "health": ModuleSpec(
        router_path="app.modules.health.router",
        prefix="",
        tags=("health",),
    ),
    "auth": ModuleSpec(
        router_path="app.modules.auth.router",
        prefix="/auth",
        tags=("auth",),
    ),
    "file_upload": ModuleSpec(
        router_path="app.modules.file_upload.router",
        prefix="/files",
        tags=("file_upload",),
    ),
    "tabular_data": ModuleSpec(
        router_path="app.modules.tabular_data.router",
        prefix="/tabular",
        tags=("tabular_data",),
    ),
    "pdf_report": ModuleSpec(
        router_path="app.modules.pdf_report.router",
        prefix="/pdf",
        tags=("pdf_report",),
    ),
    "wechat_mini_auth": ModuleSpec(
        router_path="app.modules.wechat_mini_auth.router",
        prefix="/wechat/mini-auth",
        tags=("wechat",),
        requires=("auth",),
    ),
    "wechat_pay": ModuleSpec(
        router_path="app.modules.wechat_pay.router",
        prefix="/wechat/pay",
        tags=("wechat",),
        requires=("auth",),
    ),
    "chat": ModuleSpec(
        router_path="app.modules.chat.router",
        prefix="/agent",
        tags=("agent",),
    ),
    "traces": ModuleSpec(
        router_path="app.modules.traces.router",
        prefix="/agent",
        tags=("agent",),
    ),
    "documents": ModuleSpec(
        router_path="app.modules.documents.router",
        prefix="/agent",
        tags=("agent",),
    ),
    "evals": ModuleSpec(
        router_path="app.modules.evals.router",
        prefix="/agent",
        tags=("agent",),
    ),
    "costs": ModuleSpec(
        router_path="app.modules.costs.router",
        prefix="/agent",
        tags=("agent",),
    ),
}

# ==============================
# 模块启用配置常量区（按需修改）
# ==============================

# 默认启用的核心模块
ENABLED_CORE_MODULES: tuple[str, ...] = (
    "health",
    "auth",
    "file_upload",
    "chat",
    "traces",
    "documents",
    "evals",
    "costs",
)

# 可选扩展模块（默认不启用）
ENABLED_OPTIONAL_MODULES: tuple[str, ...] = ()

# 最终启用模块清单
ENABLED_MODULES: tuple[str, ...] = (
    *ENABLED_CORE_MODULES,
    *ENABLED_OPTIONAL_MODULES,
)


def parse_enabled_modules(raw: str) -> list[str]:
    """解析逗号分隔的模块列表"""
    modules: list[str] = []
    for part in raw.split(","):
        item = part.strip()
        if item and item not in modules:
            modules.append(item)
    return modules


def validate_enabled_modules(enabled: list[str]) -> None:
    """验证模块是否存在且依赖满足"""
    for module_name in enabled:
        if module_name not in MODULE_REGISTRY:
            raise RuntimeError(f"Unknown module: '{module_name}'")

    enabled_set = set(enabled)
    for module_name in enabled:
        spec = MODULE_REGISTRY[module_name]
        for required_module in spec.requires:
            if required_module not in enabled_set:
                raise RuntimeError(f"Module '{module_name}' depends on '{required_module}'")


def get_enabled_modules() -> list[str]:
    """获取代码中配置的启用模块列表。"""
    enabled = list(ENABLED_MODULES)
    validate_enabled_modules(enabled)
    return enabled


def register_enabled_modules(app: "FastAPI", enabled_modules: list[str]) -> list[str]:
    """动态注册启用的模块路由"""
    import importlib

    validate_enabled_modules(enabled_modules)

    for module_name in enabled_modules:
        spec = MODULE_REGISTRY[module_name]
        router_module = importlib.import_module(spec.router_path)
        router = getattr(router_module, "router")
        app.include_router(router, prefix=spec.prefix, tags=list(spec.tags))

    return enabled_modules
