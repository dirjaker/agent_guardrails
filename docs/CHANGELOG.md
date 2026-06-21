# 更新日志

本文档记录 Agent Guardrails 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [未发布]

### 计划中
- 集成机器学习检测模型，增强 Prompt 注入检测能力
- 实现自定义规则引擎，支持用户自定义检测规则
- 审计日志持久化（SQLite）
- Web 管理界面
- 添加 pytest 单元测试覆盖
- 输出过滤器添加更多脱敏规则

---

## [1.0.0] - 2026-05-30

### 🎉 首次发布

#### 新增

**输入过滤模块 (`input_filter.py`)**
- Prompt 注入检测（中英文，11 种模式）
- SQL 注入检测（4 种模式）
- XSS 攻击检测（3 种模式）
- 命令注入检测（4 种模式）
- 敏感词过滤（可扩展词库）
- 置信度评分机制（0-1 分级）
- 输入过滤后自动清理危险字符

**输出过滤模块 (`output_filter.py`)**
- 邮箱地址脱敏（保留前2字符+域名）
- 手机号码脱敏（保留前3后4）
- 身份证号脱敏（保留前6后4）
- 银行卡号脱敏（保留前4后4）
- IP 地址脱敏（保留前两段）
- API Key 脱敏（保留前6后4）
- 密码检测与脱敏
- 有害内容关键词过滤
- 自定义检测模式支持

**工具防护模块 (`tool_guard.py`)**
- 工具权限管理（allow/restrict/deny 三级）
- 高风险工具自动识别（shell/exec/eval/system）
- 中风险工具频率限制（write_file/delete_file/http_request）
- 每分钟/每小时双层频率限制
- 参数危险内容检测
- 敏感操作审批队列
- 调用历史记录与统计

**审计日志模块 (`audit_logger.py`)**
- 输入/输出记录
- 工具调用记录
- 安全事件记录
- 错误事件记录
- 审批事件记录
- 安全级别分级（INFO/WARNING/ERROR/CRITICAL）
- 事件查询（按类型、按安全级别）
- 统计分析功能
- 内存管理（最大 10000 条，FIFO 淘汰）

**统一防护入口 (`guardrails.py`)**
- 整合四大模块的统一 API
- `GuardrailConfig` 配置管理
- `GuardrailResult` 统一结果返回
- `GuardAction` 防护动作枚举
- 严格模式/宽松模式切换
- 各模块可独立启停
- 工厂函数 `create_guardrails()`

**示例代码 (`examples/guardrail_demo.py`)**
- 输入过滤演示
- 输出过滤演示
- 工具防护演示
- 完整防护流程演示

#### 文档
- README.md — 项目说明与快速开始
- docs/技术文档.md — 中文技术设计文档
- docs/TECHNICAL_DOC.md — 英文技术文档
- docs/VERSION.md — 版本记录
- docs/DIRECTION.md — 项目方向指引

---

## 版本说明

- **新增**：新功能
- **变更**：已有功能的变更
- **弃用**：即将移除的功能
- **移除**：已移除的功能
- **修复**：Bug 修复
- **安全**：安全相关的变更
