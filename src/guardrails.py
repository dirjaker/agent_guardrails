"""
Guardrails 防护栏主模块
=====================

整合所有安全防护组件，提供统一的防护接口
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from .input_filter import InputFilter, FilterResult, create_input_filter
from .output_filter import OutputFilter, OutputFilterResult, create_output_filter
from .tool_guard import ToolGuard, GuardResult, create_tool_guard
from .audit_logger import AuditLogger, SecurityLevel, create_audit_logger


class GuardAction(Enum):
    """防护动作"""
    ALLOW = "allow"          # 允许
    BLOCK = "block"          # 阻止
    WARN = "warn"            # 警告
    MASK = "mask"            # 脱敏
    REQUIRE_APPROVAL = "require_approval"  # 需要审批


@dataclass
class GuardrailConfig:
    """防护栏配置"""
    enable_input_filter: bool = True
    enable_output_filter: bool = True
    enable_tool_guard: bool = True
    enable_audit_log: bool = True
    strict_mode: bool = False  # 严格模式：任何威胁都阻止


@dataclass
class GuardrailResult:
    """防护栏检查结果"""
    passed: bool  # 是否通过
    action: GuardAction
    input_result: Optional[FilterResult] = None
    output_result: Optional[OutputFilterResult] = None
    tool_result: Optional[GuardResult] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "action": self.action.value,
            "warnings": self.warnings,
            "errors": self.errors
        }


class Guardrails:
    """
    防护栏系统

    整合输入过滤、输出过滤、工具限制、审计日志
    """

    def __init__(self, config: GuardrailConfig = None):
        self.config = config or GuardrailConfig()

        # 初始化各组件
        self.input_filter = create_input_filter() if self.config.enable_input_filter else None
        self.output_filter = create_output_filter() if self.config.enable_output_filter else None
        self.tool_guard = create_tool_guard() if self.config.enable_tool_guard else None
        self.audit_logger = create_audit_logger() if self.config.enable_audit_log else None

    def check_input(self, user_input: str, user_id: str = "") -> GuardrailResult:
        """
        检查用户输入

        Args:
            user_input: 用户输入
            user_id: 用户 ID

        Returns:
            防护结果
        """
        warnings = []
        errors = []

        # 记录输入
        if self.audit_logger:
            self.audit_logger.log_input(user_id, user_input)

        # 输入过滤
        if self.input_filter:
            filter_result = self.input_filter.check(user_input)

            if not filter_result.is_safe:
                high_threats = [t for t in filter_result.threats if t.confidence >= 0.7]

                if high_threats:
                    errors.append(f"检测到 {len(high_threats)} 个高风险威胁")

                    # 记录安全事件
                    if self.audit_logger:
                        for threat in high_threats:
                            self.audit_logger.log_security(
                                f"输入威胁: {threat.description}",
                                SecurityLevel.WARNING
                            )

                    if self.config.strict_mode:
                        return GuardrailResult(
                            passed=False,
                            action=GuardAction.BLOCK,
                            input_result=filter_result,
                            errors=errors
                        )

                warnings.extend([t.description for t in filter_result.threats if t.confidence < 0.7])

            return GuardrailResult(
                passed=True,
                action=GuardAction.ALLOW if filter_result.is_safe else GuardAction.WARN,
                input_result=filter_result,
                warnings=warnings,
                errors=errors
            )

        return GuardrailResult(passed=True, action=GuardAction.ALLOW)

    def check_output(self, agent_output: str, agent_id: str = "") -> GuardrailResult:
        """
        检查 Agent 输出

        Args:
            agent_output: Agent 输出
            agent_id: Agent ID

        Returns:
            防护结果
        """
        warnings = []
        errors = []

        # 记录输出
        if self.audit_logger:
            self.audit_logger.log_output(agent_id, agent_output)

        # 输出过滤
        if self.output_filter:
            filter_result = self.output_filter.check(agent_output)

            if not filter_result.is_safe:
                errors.append(f"检测到 {len(filter_result.detections)} 个敏感信息")

                # 记录安全事件
                if self.audit_logger:
                    self.audit_logger.log_security(
                        f"输出包含敏感信息: {len(filter_result.detections)} 处",
                        SecurityLevel.WARNING
                    )

                return GuardrailResult(
                    passed=False,
                    action=GuardAction.MASK,
                    output_result=filter_result,
                    errors=errors
                )

            return GuardrailResult(
                passed=True,
                action=GuardAction.ALLOW,
                output_result=filter_result,
                warnings=warnings
            )

        return GuardrailResult(passed=True, action=GuardAction.ALLOW)

    def check_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        agent_id: str = ""
    ) -> GuardrailResult:
        """
        检查工具调用

        Args:
            tool_name: 工具名称
            parameters: 调用参数
            agent_id: Agent ID

        Returns:
            防护结果
        """
        warnings = []
        errors = []

        # 工具防护
        if self.tool_guard:
            guard_result = self.tool_guard.check(tool_name, parameters)

            if not guard_result.allowed:
                errors.append(guard_result.reason)

                # 记录安全事件
                if self.audit_logger:
                    self.audit_logger.log_security(
                        f"工具调用被阻止: {tool_name} - {guard_result.reason}",
                        SecurityLevel.WARNING
                    )

                return GuardrailResult(
                    passed=False,
                    action=GuardAction.REQUIRE_APPROVAL if "审批" in guard_result.reason else GuardAction.BLOCK,
                    tool_result=guard_result,
                    errors=errors
                )

            # 记录工具调用
            if self.audit_logger:
                self.audit_logger.log_tool_call(agent_id, tool_name, parameters)

            return GuardrailResult(
                passed=True,
                action=GuardAction.ALLOW,
                tool_result=guard_result,
                warnings=warnings
            )

        return GuardrailResult(passed=True, action=GuardAction.ALLOW)

    def get_audit_stats(self) -> Dict[str, Any]:
        """获取审计统计"""
        if self.audit_logger:
            return self.audit_logger.get_stats()
        return {}


def create_guardrails(config: GuardrailConfig = None) -> Guardrails:
    """创建防护栏系统"""
    return Guardrails(config=config)
