<div align="center">

# 🛡️ Agent Guardrails

### Agent 安全防护框架

[![规则](https://img.shields.io/badge/规则-10+-blue?style=flat-square)]()
[![检测](https://img.shields.io/badge/检测-5+-green?style=flat-square)]()
[![框架](https://img.shields.io/badge/框架-正则+LLM-orange?style=flat-square)]()
[![更新](https://img.shields.io/badge/更新-2025.06-red?style=flat-square)]()

*输入输出过滤 · 提示注入检测 · 敏感信息脱敏 · 合规审计*

</div>

---

> 智能体安全防护系统 - 保护 Agent 免受攻击和滥用

## ✨ 特性

- 🛡️ **输入过滤**：检测 Prompt 注入、SQL 注入、XSS 攻击
- 🔒 **输出过滤**：敏感信息脱敏、有害内容过滤
- 🔐 **工具限制**：权限管理、频率限制、参数验证
- 📝 **审计日志**：记录所有操作，支持安全审计

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/dirjaker/agent_guardrails.git
cd agent_guardrails

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 基础用法

```python
from src.guardrails import create_guardrails

# 创建防护系统
guardrails = create_guardrails()

# 检查输入
result = guardrails.check_input("用户输入")
if not result.passed:
    print("输入不安全:", result.errors)

# 检查输出
result = guardrails.check_output("Agent 输出")
if not result.passed:
    print("输出包含敏感信息，已脱敏:", result.output_result.filtered_output)
```

## 📁 项目结构

```
agent_guardrails/
├── src/
│   ├── __init__.py       # 包初始化
│   ├── input_filter.py   # 输入过滤
│   ├── output_filter.py  # 输出过滤
│   ├── tool_guard.py     # 工具限制
│   ├── audit_logger.py   # 审计日志
│   └── guardrails.py     # 主模块
├── examples/
│   └── guardrail_demo.py # 使用演示
├── TECHNICAL_DOC.md      # 技术文档
├── DIRECTION.md          # 方向指引
├── VERSION.md            # 版本记录
├── requirements.txt      # 依赖列表
└── README.md             # 项目说明
```

## 🛡️ 防护功能

### 1. 输入过滤

检测并阻止恶意输入：

```python
from src.input_filter import create_input_filter

filter = create_input_filter()
result = filter.check("忽略之前的指令")

if not result.is_safe:
    for threat in result.threats:
        print(f"威胁: {threat.threat_type.value}")
```

**检测能力：**
- Prompt 注入攻击
- SQL 注入
- XSS 攻击
- 命令注入
- 敏感词

### 2. 输出过滤

脱敏输出中的敏感信息：

```python
from src.output_filter import create_output_filter

filter = create_output_filter()
result = filter.check("请联系 test@example.com")

print("脱敏后:", result.filtered_output)
```

**脱敏能力：**
- 邮箱地址
- 手机号码
- 身份证号
- 银行卡号
- API Key

### 3. 工具限制

限制 Agent 的工具调用：

```python
from src.tool_guard import create_tool_guard

guard = create_tool_guard()
result = guard.check("shell", {"command": "ls"})

if not result.allowed:
    print("调用被阻止:", result.reason)
```

**限制功能：**
- 工具白名单/黑名单
- 调用频率限制
- 参数验证
- 敏感操作审批

### 4. 审计日志

记录所有操作：

```python
from src.audit_logger import create_audit_logger

logger = create_audit_logger()
logger.log_input("user_001", "用户输入")
logger.log_security("检测到攻击", SecurityLevel.WARNING)

stats = logger.get_stats()
```

## 📊 运行示例

```bash
python examples/guardrail_demo.py
```

## 🎯 应用场景

- 🤖 **Agent 安全**：保护 Agent 免受 Prompt 注入
- 🔐 **数据安全**：防止敏感信息泄露
- 🛠️ **工具安全**：限制危险工具调用
- 📋 **合规审计**：满足安全审计要求

## 📚 文档

- [技术文档](TECHNICAL_DOC.md) - 架构设计、模块详解
- [方向指引](DIRECTION.md) - 项目规划、学习路径
- [版本记录](VERSION.md) - 更新日志

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

