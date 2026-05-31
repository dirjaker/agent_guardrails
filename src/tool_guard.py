"""
Tool Guard 工具限制模块
======================

限制 Agent 的工具调用权限：
- 工具白名单/黑名单
- 参数验证
- 调用频率限制
- 敏感操作审批
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Callable
from enum import Enum
from datetime import datetime, timedelta
import json
import re


class PermissionLevel(Enum):
    """权限级别"""
    ALLOW = "allow"      # 允许
    RESTRICT = "restrict"  # 限制
    DENY = "deny"        # 拒绝


@dataclass
class ToolPermission:
    """工具权限配置"""
    tool_name: str
    permission: PermissionLevel = PermissionLevel.ALLOW
    max_calls_per_minute: int = 60
    max_calls_per_hour: int = 1000
    allowed_params: List[str] = field(default_factory=list)  # 允许的参数
    blocked_params: List[str] = field(default_factory=list)  # 禁止的参数
    require_approval: bool = False  # 是否需要审批

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "permission": self.permission.value,
            "max_calls_per_minute": self.max_calls_per_minute,
            "require_approval": self.require_approval
        }


@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
            "approved": self.approved
        }


@dataclass
class GuardResult:
    """防护结果"""
    allowed: bool
    reason: str = ""
    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "tool_name": self.tool_name
        }


class ToolGuard:
    """
    工具防护器

    管理和限制 Agent 的工具调用
    """

    def __init__(self):
        # 工具权限配置
        self.permissions: Dict[str, ToolPermission] = {}

        # 调用历史
        self.call_history: List[ToolCall] = []

        # 审批队列
        self.approval_queue: List[ToolCall] = []

        # 默认权限
        self.default_permission = PermissionLevel.ALLOW

        # 初始化默认工具权限
        self._init_default_permissions()

    def _init_default_permissions(self):
        """初始化默认工具权限"""
        # 高风险工具
        high_risk_tools = ["shell", "exec", "eval", "system"]
        for tool in high_risk_tools:
            self.permissions[tool] = ToolPermission(
                tool_name=tool,
                permission=PermissionLevel.RESTRICT,
                max_calls_per_minute=5,
                require_approval=True
            )

        # 中风险工具
        medium_risk_tools = ["write_file", "delete_file", "http_request"]
        for tool in medium_risk_tools:
            self.permissions[tool] = ToolPermission(
                tool_name=tool,
                permission=PermissionLevel.ALLOW,
                max_calls_per_minute=30
            )

    def check(self, tool_name: str, parameters: Dict[str, Any] = None) -> GuardResult:
        """
        检查工具调用是否允许

        Args:
            tool_name: 工具名称
            parameters: 调用参数

        Returns:
            防护结果
        """
        parameters = parameters or {}

        # 1. 检查工具权限
        permission = self.permissions.get(tool_name)
        if permission and permission.permission == PermissionLevel.DENY:
            return GuardResult(
                allowed=False,
                reason=f"工具 {tool_name} 被禁止使用",
                tool_name=tool_name,
                parameters=parameters
            )

        # 2. 检查调用频率
        if not self._check_rate_limit(tool_name, permission):
            return GuardResult(
                allowed=False,
                reason=f"工具 {tool_name} 调用频率超限",
                tool_name=tool_name,
                parameters=parameters,
                suggestion="请稍后再试"
            )

        # 3. 检查参数
        param_check = self._check_parameters(tool_name, parameters, permission)
        if not param_check.allowed:
            return param_check

        # 4. 检查是否需要审批
        if permission and permission.require_approval:
            return GuardResult(
                allowed=False,
                reason=f"工具 {tool_name} 需要审批",
                tool_name=tool_name,
                parameters=parameters,
                suggestion="请提交审批申请"
            )

        # 记录调用
        self._record_call(tool_name, parameters)

        return GuardResult(
            allowed=True,
            tool_name=tool_name,
            parameters=parameters
        )

    def _check_rate_limit(self, tool_name: str, permission: Optional[ToolPermission]) -> bool:
        """检查调用频率"""
        if not permission:
            return True

        now = datetime.now()

        # 检查每分钟限制
        minute_ago = now - timedelta(minutes=1)
        recent_calls = [
            c for c in self.call_history
            if c.tool_name == tool_name and c.timestamp > minute_ago
        ]

        if len(recent_calls) >= permission.max_calls_per_minute:
            return False

        # 检查每小时限制
        hour_ago = now - timedelta(hours=1)
        hourly_calls = [
            c for c in self.call_history
            if c.tool_name == tool_name and c.timestamp > hour_ago
        ]

        if len(hourly_calls) >= permission.max_calls_per_hour:
            return False

        return True

    def _check_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        permission: Optional[ToolPermission]
    ) -> GuardResult:
        """检查参数"""
        if not permission:
            return GuardResult(allowed=True, tool_name=tool_name, parameters=parameters)

        # 检查禁止的参数
        for param_name in parameters:
            if param_name in permission.blocked_params:
                return GuardResult(
                    allowed=False,
                    reason=f"参数 {param_name} 被禁止",
                    tool_name=tool_name,
                    parameters=parameters
                )

        # 检查参数值中的危险内容
        for param_name, param_value in parameters.items():
            if isinstance(param_value, str):
                if self._contains_dangerous_content(param_value):
                    return GuardResult(
                        allowed=False,
                        reason=f"参数 {param_name} 包含危险内容",
                        tool_name=tool_name,
                        parameters=parameters
                    )

        return GuardResult(allowed=True, tool_name=tool_name, parameters=parameters)

    def _contains_dangerous_content(self, text: str) -> bool:
        """检测危险内容"""
        dangerous_patterns = [
            r"(rm\s+-rf|format\s+c:)",
            r"(DROP\s+TABLE|DELETE\s+FROM)",
            r"(<script>)",
            r"(sudo\s+)",
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _record_call(self, tool_name: str, parameters: Dict[str, Any]):
        """记录工具调用"""
        call = ToolCall(
            tool_name=tool_name,
            parameters=parameters
        )
        self.call_history.append(call)

        # 保留最近的调用记录
        if len(self.call_history) > 10000:
            self.call_history = self.call_history[-5000:]

    def add_permission(self, permission: ToolPermission):
        """添加工具权限"""
        self.permissions[permission.tool_name] = permission

    def approve_call(self, call: ToolCall):
        """审批工具调用"""
        call.approved = True
        self.approval_queue.remove(call) if call in self.approval_queue else None

    def get_call_stats(self) -> Dict[str, Any]:
        """获取调用统计"""
        stats = {}
        for call in self.call_history:
            if call.tool_name not in stats:
                stats[call.tool_name] = 0
            stats[call.tool_name] += 1
        return stats


def create_tool_guard() -> ToolGuard:
    """创建工具防护器"""
    return ToolGuard()
