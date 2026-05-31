"""
Audit Logger 审计日志模块
========================

记录所有 Agent 操作：
- 输入/输出记录
- 工具调用记录
- 安全事件记录
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class EventType(Enum):
    """事件类型"""
    INPUT = "input"              # 用户输入
    OUTPUT = "output"            # Agent 输出
    TOOL_CALL = "tool_call"      # 工具调用
    SECURITY = "security"        # 安全事件
    ERROR = "error"              # 错误事件
    APPROVAL = "approval"        # 审批事件


class SecurityLevel(Enum):
    """安全级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """审计事件"""
    id: str = ""
    event_type: EventType = EventType.INPUT
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    agent_id: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.INFO

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "content": self.content[:200],
            "security_level": self.security_level.value
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """
    审计日志记录器

    记录所有 Agent 操作，用于安全审计和问题追踪
    """

    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events: List[AuditEvent] = []
        self._event_counter = 0

    def log_input(self, user_id: str, content: str, metadata: Dict = None) -> AuditEvent:
        """记录用户输入"""
        event = self._create_event(
            event_type=EventType.INPUT,
            user_id=user_id,
            content=content,
            metadata=metadata or {}
        )
        self.events.append(event)
        self._trim_events()
        return event

    def log_output(self, agent_id: str, content: str, metadata: Dict = None) -> AuditEvent:
        """记录 Agent 输出"""
        event = self._create_event(
            event_type=EventType.OUTPUT,
            agent_id=agent_id,
            content=content,
            metadata=metadata or {}
        )
        self.events.append(event)
        self._trim_events()
        return event

    def log_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any = None
    ) -> AuditEvent:
        """记录工具调用"""
        content = f"调用工具: {tool_name}"
        metadata = {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": str(result)[:500] if result else None
        }

        event = self._create_event(
            event_type=EventType.TOOL_CALL,
            agent_id=agent_id,
            content=content,
            metadata=metadata
        )
        self.events.append(event)
        self._trim_events()
        return event

    def log_security(
        self,
        description: str,
        security_level: SecurityLevel = SecurityLevel.WARNING,
        metadata: Dict = None
    ) -> AuditEvent:
        """记录安全事件"""
        event = self._create_event(
            event_type=EventType.SECURITY,
            content=description,
            metadata=metadata or {},
            security_level=security_level
        )
        self.events.append(event)
        self._trim_events()
        return event

    def log_error(self, error: str, metadata: Dict = None) -> AuditEvent:
        """记录错误事件"""
        event = self._create_event(
            event_type=EventType.ERROR,
            content=error,
            metadata=metadata or {},
            security_level=SecurityLevel.ERROR
        )
        self.events.append(event)
        self._trim_events()
        return event

    def _create_event(
        self,
        event_type: EventType,
        content: str,
        user_id: str = "",
        agent_id: str = "",
        metadata: Dict = None,
        security_level: SecurityLevel = SecurityLevel.INFO
    ) -> AuditEvent:
        """创建审计事件"""
        self._event_counter += 1
        return AuditEvent(
            id=f"evt_{self._event_counter:06d}",
            event_type=event_type,
            user_id=user_id,
            agent_id=agent_id,
            content=content,
            metadata=metadata or {},
            security_level=security_level
        )

    def _trim_events(self):
        """裁剪事件列表"""
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        security_level: Optional[SecurityLevel] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """获取事件列表"""
        events = self.events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if security_level:
            events = [e for e in events if e.security_level == security_level]

        return events[-limit:]

    def get_security_events(self, limit: int = 50) -> List[AuditEvent]:
        """获取安全事件"""
        return self.get_events(event_type=EventType.SECURITY, limit=limit)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_events": len(self.events),
            "by_type": {},
            "by_security_level": {}
        }

        for event in self.events:
            # 按类型统计
            type_name = event.event_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

            # 按安全级别统计
            level_name = event.security_level.value
            stats["by_security_level"][level_name] = stats["by_security_level"].get(level_name, 0) + 1

        return stats

    def clear(self):
        """清空日志"""
        self.events.clear()


def create_audit_logger(max_events: int = 10000) -> AuditLogger:
    """创建审计日志记录器"""
    return AuditLogger(max_events=max_events)
