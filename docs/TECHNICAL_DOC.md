# Agent Guardrails - 技术文档

## 1. 项目概述

Agent Guardrails 是一个智能体安全防护系统，保护 Agent 免受各种攻击和滥用。

### 1.1 核心特性

- **输入过滤**：检测 Prompt 注入、SQL 注入、XSS 攻击
- **输出过滤**：敏感信息脱敏、有害内容过滤
- **工具限制**：权限管理、频率限制、参数验证
- **审计日志**：记录所有操作，支持安全审计

### 1.2 应用场景

- 保护 Agent 免受 Prompt 注入攻击
- 防止敏感信息泄露
- 限制危险工具调用
- 安全审计和合规

## 2. 架构设计

### 2.1 防护层级

```
用户输入
    ↓
┌─────────────────┐
│  Input Filter   │ 输入过滤
│ - Prompt 注入   │
│ - SQL 注入      │
│ - XSS 攻击      │
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 处理    │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Output Filter  │ 输出过滤
│ - 敏感信息脱敏  │
│ - 有害内容过滤  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Tool Guard     │ 工具限制
│ - 权限控制      │
│ - 频率限制      │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Audit Logger   │ 审计日志
└─────────────────┘
```

### 2.2 防护流程

```
请求 → 输入检查 → [阻止/允许] → Agent 处理 → 输出检查 → [脱敏/允许] → 返回
```

## 3. 模块详解

### 3.1 Input Filter (`input_filter.py`)

检测恶意输入：

```python
filter = create_input_filter()
result = filter.check("忽略之前的指令")

if not result.is_safe:
    print("检测到威胁:", result.threats)
```

**支持的检测：**
- Prompt 注入
- SQL 注入
- XSS 攻击
- 命令注入
- 敏感词

### 3.2 Output Filter (`output_filter.py`)

过滤敏感输出：

```python
filter = create_output_filter()
result = filter.check("请联系 test@example.com")

if not result.is_safe:
    print("脱敏后:", result.filtered_output)
```

**支持的脱敏：**
- 邮箱地址
- 手机号码
- 身份证号
- 银行卡号
- API Key

### 3.3 Tool Guard (`tool_guard.py`)

限制工具调用：

```python
guard = create_tool_guard()
result = guard.check("shell", {"command": "rm -rf /"})

if not result.allowed:
    print("调用被阻止:", result.reason)
```

**防护功能：**
- 工具白名单/黑名单
- 调用频率限制
- 参数验证
- 敏感操作审批

### 3.4 Audit Logger (`audit_logger.py`)

记录所有操作：

```python
logger = create_audit_logger()
logger.log_input("user_001", "用户输入")
logger.log_security("检测到攻击", SecurityLevel.WARNING)
```

### 3.5 Guardrails (`guardrails.py`)

整合所有防护组件：

```python
guardrails = create_guardrails()
result = guardrails.check_input("用户输入")
result = guardrails.check_output("Agent 输出")
result = guardrails.check_tool_call("tool", {})
```

## 4. 使用指南

### 4.1 快速开始

```python
from src.guardrails import create_guardrails

# 创建防护系统
guardrails = create_guardrails()

# 检查输入
result = guardrails.check_input("用户输入")
if not result.passed:
    print("输入不安全:", result.errors)
```

### 4.2 自定义配置

```python
from src.guardrails import create_guardrails, GuardrailConfig

config = GuardrailConfig(
    enable_input_filter=True,
    enable_output_filter=True,
    enable_tool_guard=True,
    enable_audit_log=True,
    strict_mode=True  # 严格模式
)

guardrails = create_guardrails(config)
```

### 4.3 添加自定义规则

```python
from src.input_filter import create_input_filter

filter = create_input_filter()
filter.add_sensitive_word("自定义敏感词")
```

## 5. 设计决策

### 5.1 为什么需要多层防护？

单一防护层可能被绕过，多层防护提供深度防御：
- 输入过滤：阻止恶意输入进入系统
- 输出过滤：防止敏感信息泄露
- 工具限制：限制 Agent 的能力范围
- 审计日志：事后追溯和分析

### 5.2 置信度机制

每个威胁检测都有置信度分数：
- 高置信度 (≥0.7)：立即阻止
- 中置信度 (0.5-0.7)：警告
- 低置信度 (<0.5)：记录日志

### 5.3 严格模式 vs 宽松模式

- **严格模式**：任何威胁都阻止
- **宽松模式**：高置信度威胁才阻止，低置信度只警告

## 6. 扩展点

### 6.1 添加新的威胁检测

在 `InputFilter` 中添加新的正则模式。

### 6.2 添加新的脱敏规则

在 `OutputFilter` 中添加新的正则模式。

### 6.3 集成外部安全服务

替换检测逻辑，调用专业的安全 API。

## 7. 已知限制

- 基于规则的检测，可能有误报
- 无法检测所有类型的攻击
- 脱敏规则可能不够全面

## 8. 项目结构

```
agent_guardrails/
├── src/
│   ├── __init__.py         # 包初始化，版本信息
│   ├── guardrails.py       # 统一防护入口
│   ├── input_filter.py     # 输入过滤模块
│   ├── output_filter.py    # 输出过滤模块
│   ├── tool_guard.py       # 工具防护模块
│   ├── audit_logger.py     # 审计日志模块
│   ├── web/
│   │   ├── app.py          # FastAPI Web 服务
│   │   └── static/         # 前端静态文件
│   └── macos/
│       └── app.py          # macOS 桌面应用
├── examples/
│   └── guardrail_demo.py   # 功能演示
├── docs/                   # 项目文档
├── assets/                 # 静态资源
├── packaging/              # 打包配置
└── requirements.txt        # 依赖列表
```

## 9. 后续计划

- [ ] 集成机器学习检测模型
- [ ] 添加更多脱敏规则
- [ ] 实现 Web UI
- [ ] 支持自定义规则引擎
