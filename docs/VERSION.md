# Agent Guardrails 版本记录

## v1.0.0 (2026-05-30)

### 🎉 初始版本

#### 核心功能
- **Input Filter 模块** (`src/input_filter.py`, 244 行)
  - Prompt 注入检测（中英文，11 种模式）
  - SQL 注入检测（4 种模式）
  - XSS 攻击检测（3 种模式）
  - 命令注入检测（4 种模式）
  - 敏感词过滤（可扩展词库）
  - 置信度评分机制（0-1 分级）

- **Output Filter 模块** (`src/output_filter.py`, 199 行)
  - 邮箱地址脱敏
  - 手机号码脱敏
  - 身份证号脱敏
  - 银行卡号脱敏
  - IP 地址脱敏
  - API Key / 密码脱敏
  - 有害内容过滤
  - 自定义检测模式

- **Tool Guard 模块** (`src/tool_guard.py`, 291 行)
  - 工具权限管理（allow/restrict/deny）
  - 高/中/低风险工具分级
  - 每分钟/每小时双层频率限制
  - 参数危险内容检测
  - 敏感操作审批队列

- **Audit Logger 模块** (`src/audit_logger.py`, 226 行)
  - 输入/输出/工具调用/安全事件记录
  - 安全级别分级（INFO→CRITICAL）
  - 事件查询与统计分析
  - 内存管理（最大 10000 条）

- **Guardrails 主模块** (`src/guardrails.py`, 240 行)
  - 整合所有防护组件
  - 统一 API 接口
  - 严格模式/宽松模式切换
  - 配置驱动的模块启停

#### 扩展功能
- **Web API 服务** (`src/web/app.py`, 137 行)
  - FastAPI REST API
  - 7 个 API 端点
  - 仪表盘页面

- **macOS 桌面应用** (`src/macos/app.py`, 141 行)
  - tkinter GUI
  - 输入检查/输出脱敏/工具检查三个功能页

#### 示例代码
- `examples/guardrail_demo.py` — 完整功能演示（140 行）

#### 文档
- `README.md` — 项目说明与快速开始
- `docs/技术文档.md` — 中文技术设计文档
- `docs/TECHNICAL_DOC.md` — 英文技术文档
- `docs/DEVELOPMENT.md` — 开发环境搭建指南
- `docs/CHANGELOG.md` — 更新日志
- `docs/DIRECTION.md` — 项目方向指引
- `REVIEW.md` — 代码审查报告

---

## 后续计划

### v1.1.0 (计划中)
- [ ] 集成机器学习检测模型
- [ ] 添加更多脱敏规则
- [ ] 支持自定义规则引擎
- [ ] 添加 pytest 单元测试

### v1.2.0 (计划中)
- [ ] SQLite 持久化审计日志
- [ ] Web UI 管理界面
- [ ] 实时告警功能

### v2.0.0 (远期)
- [ ] 多租户支持
- [ ] 与 SIEM 系统集成
- [ ] 合规报告生成
- [ ] LLM 深度检测集成
