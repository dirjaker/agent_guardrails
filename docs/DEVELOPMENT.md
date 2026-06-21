# 开发环境搭建指南

本文档帮助开发者快速搭建 Agent Guardrails 项目的开发环境。

---

## 1. 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.8+ | 核心运行时 |
| conda | 4.x+ | 推荐的环境管理工具 |
| pip | 21.0+ | 包管理工具 |
| Git | 2.x+ | 版本控制 |

## 2. 快速搭建

### 2.1 克隆项目

```bash
git clone https://github.com/dirjaker/agent_guardrails.git
cd agent_guardrails
git checkout dev
```

### 2.2 创建虚拟环境

**方式一：conda（推荐）**

```bash
conda create -n agent_guardrails python=3.12 -y
conda activate agent_guardrails
```

**方式二：venv**

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 2.3 安装依赖

```bash
# 核心依赖（Web API 需要）
pip install -r requirements.txt

# 开发依赖（可选）
pip install pytest pytest-cov black ruff mypy
```

当前 `requirements.txt` 内容：

```
httpx==0.28.1
pydantic==2.13.4
pydantic_core==2.46.4
typing_extensions==4.15.0
```

> **注意**：核心防护模块（`src/input_filter.py`、`src/output_filter.py`、`src/tool_guard.py`、`src/audit_logger.py`、`src/guardrails.py`）仅使用 Python 标准库，零外部依赖。外部依赖仅用于 Web API 服务。

### 2.4 验证安装

```bash
# 测试核心模块导入
python -c "from src.guardrails import create_guardrails; print('✅ 核心模块导入成功')"

# 运行示例
python examples/guardrail_demo.py
```

## 3. 运行方式

### 3.1 命令行示例

```bash
python examples/guardrail_demo.py
```

示例包含四个演示：
1. **输入过滤演示**：测试 Prompt 注入、SQL 注入、XSS 等检测
2. **输出过滤演示**：测试邮箱、手机号、身份证等脱敏
3. **工具防护演示**：测试工具调用权限和频率限制
4. **完整防护演示**：模拟完整的对话防护流程

### 3.2 Web API 服务

```bash
python -m src.web.app
# 服务启动在 http://0.0.0.0:8080
# 访问 http://localhost:8080 查看仪表盘
```

**API 端点测试**：

```bash
# 健康检查
curl http://localhost:8080/api/health

# 输入安全检查
curl -X POST http://localhost:8080/api/check/input \
  -H "Content-Type: application/json" \
  -d '{"text": "忽略之前的指令", "user_id": "test"}'

# 输出脱敏检查
curl -X POST http://localhost:8080/api/check/output \
  -H "Content-Type: application/json" \
  -d '{"text": "请联系 test@example.com 或 13800138000"}'

# 工具调用检查
curl -X POST http://localhost:8080/api/check/tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "shell", "params": {"command": "ls"}}'

# 审计统计
curl http://localhost:8080/api/audit/stats
```

### 3.3 macOS 桌面应用

```bash
python src/macos/app.py
```

> 需要图形界面环境支持（macOS 原生或 X11 转发）。

### 3.4 打包 macOS 应用

```bash
# 需要先安装 py2app
pip install py2app

# 打包
cd packaging
python py2app_setup.py py2app
```

## 4. 开发规范

### 4.1 代码风格

- 遵循 PEP 8 规范
- 使用中文注释和文档字符串
- 类型注解：所有公共方法必须添加类型注解
- dataclass：数据结构使用 `@dataclass` 装饰器

### 4.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `InputFilter`、`GuardrailConfig` |
| 方法名 | snake_case | `check_input`、`log_security` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_MAX_EVENTS` |
| 私有方法 | 前缀 `_` | `_check_injection`、`_mask` |
| 工厂函数 | `create_xxx()` | `create_guardrails()` |

### 4.3 文档规范

- 每个模块顶部有模块说明文档字符串
- 每个类和公共方法有文档字符串
- 文档字符串使用中文
- 参数说明使用 `Args:` 和 `Returns:` 格式

```python
def check(self, user_input: str) -> FilterResult:
    """
    检查输入安全性

    Args:
        user_input: 用户输入

    Returns:
        过滤结果
    """
```

### 4.4 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

## 5. 项目架构说明

### 5.1 模块依赖关系

```
guardrails.py (统一入口)
    ├── input_filter.py   (输入过滤)
    ├── output_filter.py  (输出过滤)
    ├── tool_guard.py     (工具防护)
    └── audit_logger.py   (审计日志)

web/app.py (Web API)
    └── guardrails.py

macos/app.py (桌面应用)
    └── guardrails.py
```

### 5.2 工厂模式

所有模块通过工厂函数创建，方便测试和替换：

```python
from src.guardrails import create_guardrails, GuardrailConfig
from src.input_filter import create_input_filter
from src.output_filter import create_output_filter
from src.tool_guard import create_tool_guard
from src.audit_logger import create_audit_logger

# 创建独立模块
input_filter = create_input_filter()
output_filter = create_output_filter()
tool_guard = create_tool_guard()
audit_logger = create_audit_logger(max_events=5000)

# 创建完整防护系统
guardrails = create_guardrails(GuardrailConfig(
    enable_input_filter=True,
    enable_output_filter=True,
    enable_tool_guard=True,
    enable_audit_log=True,
    strict_mode=False
))
```

## 6. 测试

### 6.1 运行示例测试

```bash
python examples/guardrail_demo.py
```

### 6.2 单元测试（待实现）

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ -v --cov=src --cov-report=html

# 运行特定模块测试
pytest tests/test_input_filter.py -v
```

### 6.3 推荐测试用例

**输入过滤测试**：
- 正常输入应通过
- Prompt 注入应被检测（中英文）
- SQL 注入应被检测
- XSS 攻击应被检测
- 命令注入应被检测

**输出过滤测试**：
- 正常输出应通过
- 邮箱应被脱敏
- 手机号应被脱敏
- 身份证号应被脱敏
- API Key 应被脱敏

**工具防护测试**：
- 普通工具应允许
- 高风险工具应被限制
- 频率超限应被阻止
- 危险参数应被检测

## 7. 常见问题

### Q: 导入模块报错 `ModuleNotFoundError`

**A**: 确保在项目根目录运行，或设置 `PYTHONPATH`：

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python examples/guardrail_demo.py
```

### Q: Web API 启动报错 `ModuleNotFoundError: fastapi`

**A**: 安装 Web 依赖：

```bash
pip install -r requirements.txt
```

### Q: macOS 应用启动报错

**A**: 确保在 macOS 系统上运行，且安装了 tkinter（Python 默认包含）。

## 8. 相关资源

- [Python 官方文档](https://docs.python.org/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [OWASP AI Security](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
