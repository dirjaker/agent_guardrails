"""
Output Filter 输出过滤模块
=========================

检测和过滤敏感输出：
- 敏感信息脱敏
- 有害内容过滤
- 输出格式验证
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import re


class SensitiveType(Enum):
    """敏感信息类型"""
    EMAIL = "email"
    PHONE = "phone"
    ID_CARD = "id_card"
    BANK_CARD = "bank_card"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    PASSWORD = "password"
    CUSTOM = "custom"


@dataclass
class SensitiveDetection:
    """敏感信息检测结果"""
    sensitive_type: SensitiveType
    original_text: str
    masked_text: str
    location: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.sensitive_type.value,
            "original": self.original_text[:10] + "...",
            "masked": self.masked_text
        }


@dataclass
class OutputFilterResult:
    """输出过滤结果"""
    is_safe: bool
    detections: List[SensitiveDetection] = field(default_factory=list)
    filtered_output: str = ""
    original_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "detection_count": len(self.detections),
            "detections": [d.to_dict() for d in self.detections]
        }


class OutputFilter:
    """
    输出过滤器

    检测和脱敏输出中的敏感信息
    """

    def __init__(self):
        # 正则模式
        self.patterns = {
            SensitiveType.EMAIL: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            SensitiveType.PHONE: r'1[3-9]\d{9}',
            SensitiveType.ID_CARD: r'\d{17}[\dXx]',
            SensitiveType.BANK_CARD: r'\d{16,19}',
            SensitiveType.IP_ADDRESS: r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            SensitiveType.API_KEY: r'(sk|pk|api)[_-]?[a-zA-Z0-9]{20,}',
            SensitiveType.PASSWORD: r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+',
        }

        # 有害内容关键词
        self.harmful_keywords: Set[str] = {
            "暴力", "违法", "色情", "赌博", "毒品",
            "暴力", "illegal", "porn", "gambling", "drug"
        }

    def check(self, output: str) -> OutputFilterResult:
        """
        检查输出安全性

        Args:
            output: Agent 输出

        Returns:
            过滤结果
        """
        detections = []

        # 检测敏感信息
        for sensitive_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, output)
            for match in matches:
                original = match.group()
                masked = self._mask(original, sensitive_type)
                detections.append(SensitiveDetection(
                    sensitive_type=sensitive_type,
                    original_text=original,
                    masked_text=masked,
                    location=f"position {match.start()}-{match.end()}"
                ))

        # 检测有害内容
        harmful_detections = self._check_harmful_content(output)
        detections.extend(harmful_detections)

        # 生成过滤后的输出
        filtered_output = self._apply_filters(output, detections)

        return OutputFilterResult(
            is_safe=len(detections) == 0,
            detections=detections,
            filtered_output=filtered_output,
            original_output=output
        )

    def _mask(self, text: str, sensitive_type: SensitiveType) -> str:
        """脱敏处理"""
        if sensitive_type == SensitiveType.EMAIL:
            parts = text.split('@')
            if len(parts) == 2:
                username = parts[0]
                if len(username) > 2:
                    return username[:2] + '***@' + parts[1]
                return '***@' + parts[1]

        elif sensitive_type == SensitiveType.PHONE:
            return text[:3] + '****' + text[7:]

        elif sensitive_type == SensitiveType.ID_CARD:
            return text[:6] + '********' + text[14:]

        elif sensitive_type == SensitiveType.BANK_CARD:
            return text[:4] + ' **** **** ' + text[-4:]

        elif sensitive_type == SensitiveType.IP_ADDRESS:
            parts = text.split('.')
            return parts[0] + '.' + parts[1] + '.*.*'

        elif sensitive_type == SensitiveType.API_KEY:
            return text[:6] + '...' + text[-4:]

        elif sensitive_type == SensitiveType.PASSWORD:
            return '********'

        return '***'

    def _check_harmful_content(self, text: str) -> List[SensitiveDetection]:
        """检测有害内容"""
        detections = []
        text_lower = text.lower()

        for keyword in self.harmful_keywords:
            if keyword.lower() in text_lower:
                detections.append(SensitiveDetection(
                    sensitive_type=SensitiveType.CUSTOM,
                    original_text=keyword,
                    masked_text='***',
                    location="有害内容"
                ))

        return detections

    def _apply_filters(self, text: str, detections: List[SensitiveDetection]) -> str:
        """应用过滤"""
        filtered = text

        # 按位置倒序替换，避免位置偏移
        sorted_detections = sorted(
            detections,
            key=lambda d: d.original_text,
            reverse=True
        )

        for detection in sorted_detections:
            filtered = filtered.replace(detection.original_text, detection.masked_text)

        return filtered

    def add_harmful_keyword(self, keyword: str):
        """添加有害关键词"""
        self.harmful_keywords.add(keyword)

    def add_custom_pattern(self, pattern_name: str, pattern: str):
        """添加自定义检测模式"""
        self.patterns[SensitiveType.CUSTOM] = pattern


def create_output_filter() -> OutputFilter:
    """创建输出过滤器"""
    return OutputFilter()
