"""
Input Filter 输入过滤模块
========================

检测和过滤恶意输入：
- Prompt 注入检测
- 敏感词过滤
- 输入格式验证
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import re


class ThreatType(Enum):
    """威胁类型"""
    PROMPT_INJECTION = "prompt_injection"  # Prompt 注入
    SENSITIVE_WORD = "sensitive_word"      # 敏感词
    SQL_INJECTION = "sql_injection"        # SQL 注入
    XSS_ATTACK = "xss_attack"            # XSS 攻击
    COMMAND_INJECTION = "command_injection"  # 命令注入
    MALICIOUS_INPUT = "malicious_input"   # 恶意输入


@dataclass
class ThreatDetection:
    """威胁检测结果"""
    threat_type: ThreatType
    confidence: float  # 0-1
    description: str
    location: str = ""  # 威胁位置
    suggestion: str = ""  # 处理建议

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_type": self.threat_type.value,
            "confidence": self.confidence,
            "description": self.description,
            "location": self.location
        }


@dataclass
class FilterResult:
    """过滤结果"""
    is_safe: bool
    threats: List[ThreatDetection] = field(default_factory=list)
    filtered_input: str = ""
    original_input: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "threat_count": len(self.threats),
            "threats": [t.to_dict() for t in self.threats]
        }


class InputFilter:
    """
    输入过滤器

    检测各种类型的恶意输入
    """

    def __init__(self):
        # Prompt 注入模式
        self.injection_patterns = [
            r"忽略(之前|上面|以前)的(指令|提示|规则)",
            r"ignore( previous| above| earlier) (instructions|prompts|rules)",
            r"你(现在|从现在开始)是",
            r"you are now",
            r"假装(你是|你是)",
            r"pretend (you are|you're)",
            r"进入(开发者|调试|管理员)模式",
            r"(enter|enable) (developer|debug|admin) mode",
            r"system\s*:\s*",
            r"assistant\s*:\s*",
            r"user\s*:\s*",
        ]

        # 敏感词列表
        self.sensitive_words: Set[str] = {
            "密码", "password", "secret", "token", "api_key",
            "私钥", "private_key", "credential", "认证"
        }

        # SQL 注入模式
        self.sql_patterns = [
            r"('\s*(OR|AND)\s*')",
            r"(;\s*(DROP|DELETE|UPDATE|INSERT)\s)",
            r"(UNION\s+SELECT)",
            r"(--\s*$)",
        ]

        # XSS 模式
        self.xss_patterns = [
            r"(<script[^>]*>)",
            r"(javascript\s*:)",
            r"(on\w+\s*=)",
        ]

        # 命令注入模式
        self.command_patterns = [
            r"(;\s*(ls|cat|rm|wget|curl)\s)",
            r"(\|\s*(ls|cat|rm|wget|curl)\s)",
            r"(`[^`]+`)",
            r"(\$\([^)]+\))",
        ]

    def check(self, user_input: str) -> FilterResult:
        """
        检查输入安全性

        Args:
            user_input: 用户输入

        Returns:
            过滤结果
        """
        threats = []

        # 检测 Prompt 注入
        injection_threats = self._check_injection(user_input)
        threats.extend(injection_threats)

        # 检测敏感词
        sensitive_threats = self._check_sensitive_words(user_input)
        threats.extend(sensitive_threats)

        # 检测 SQL 注入
        sql_threats = self._check_sql_injection(user_input)
        threats.extend(sql_threats)

        # 检测 XSS
        xss_threats = self._check_xss(user_input)
        threats.extend(xss_threats)

        # 检测命令注入
        cmd_threats = self._check_command_injection(user_input)
        threats.extend(cmd_threats)

        # 判断是否安全
        is_safe = len(threats) == 0 or all(t.confidence < 0.5 for t in threats)

        return FilterResult(
            is_safe=is_safe,
            threats=threats,
            filtered_input=self._filter_input(user_input, threats),
            original_input=user_input
        )

    def _check_injection(self, text: str) -> List[ThreatDetection]:
        """检测 Prompt 注入"""
        threats = []
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(ThreatDetection(
                    threat_type=ThreatType.PROMPT_INJECTION,
                    confidence=0.8,
                    description=f"检测到 Prompt 注入模式: {pattern}",
                    suggestion="忽略此输入或要求用户重新表述"
                ))
        return threats

    def _check_sensitive_words(self, text: str) -> List[ThreatDetection]:
        """检测敏感词"""
        threats = []
        text_lower = text.lower()
        for word in self.sensitive_words:
            if word.lower() in text_lower:
                threats.append(ThreatDetection(
                    threat_type=ThreatType.SENSITIVE_WORD,
                    confidence=0.6,
                    description=f"包含敏感词: {word}",
                    suggestion="移除或脱敏处理"
                ))
        return threats

    def _check_sql_injection(self, text: str) -> List[ThreatDetection]:
        """检测 SQL 注入"""
        threats = []
        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(ThreatDetection(
                    threat_type=ThreatType.SQL_INJECTION,
                    confidence=0.9,
                    description="检测到 SQL 注入模式",
                    suggestion="使用参数化查询"
                ))
        return threats

    def _check_xss(self, text: str) -> List[ThreatDetection]:
        """检测 XSS 攻击"""
        threats = []
        for pattern in self.xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(ThreatDetection(
                    threat_type=ThreatType.XSS_ATTACK,
                    confidence=0.9,
                    description="检测到 XSS 攻击模式",
                    suggestion="对输出进行 HTML 转义"
                ))
        return threats

    def _check_command_injection(self, text: str) -> List[ThreatDetection]:
        """检测命令注入"""
        threats = []
        for pattern in self.command_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(ThreatDetection(
                    threat_type=ThreatType.COMMAND_INJECTION,
                    confidence=0.85,
                    description="检测到命令注入模式",
                    suggestion="使用白名单验证输入"
                ))
        return threats

    def _filter_input(self, text: str, threats: List[ThreatDetection]) -> str:
        """过滤输入"""
        filtered = text

        # 如果有高置信度威胁，进行过滤
        high_threats = [t for t in threats if t.confidence >= 0.7]
        if high_threats:
            # 移除危险字符
            filtered = re.sub(r'[<>&;|`$]', '', filtered)

        return filtered

    def add_sensitive_word(self, word: str):
        """添加敏感词"""
        self.sensitive_words.add(word)

    def remove_sensitive_word(self, word: str):
        """移除敏感词"""
        self.sensitive_words.discard(word)


def create_input_filter() -> InputFilter:
    """创建输入过滤器"""
    return InputFilter()
