# Agent Guardrails — 代码审查报告

> 审查日期：2026-06-21  
> 项目路径：`/home/dirjaker/myprojects/agent_guardrails`  
> 审查范围：10 个 Python 源文件

---

## 🔴 致命问题

### 1. CORS 配置允许所有来源
- **文件**：`src/web/app.py` **第 24 行**
- **问题**：`allow_origins=["*"]` 允许任意域名跨域调用安全防护 API。攻击者可从恶意网站发起请求，利用防护系统探测输入过滤规则（绕过防护）。
- **修复建议**：限制为实际前端域名，生产环境使用环境变量配置。

### 2. 安全防护 API 无认证
- **文件**：`src/web/app.py` **第 61-110 行**
- **问题**：作为安全防护系统，所有安全检查端点（`/api/check/input`、`/api/check/output`、`/api/check/tool`）和审计统计端点（`/api/audit/stats`）均无任何认证机制。任何人可调用这些接口探测安全规则。
- **修复建议**：添加 API Key 或 Bearer Token 认证；审计端点应仅限管理员访问。

### 3. 默认权限为 ALLOW（未知工具全部放行）
- **文件**：`src/tool_guard.py` **第 100 行**
- **问题**：`self.default_permission = PermissionLevel.ALLOW` 意味着未配置权限的工具默认允许调用。结合 `check()` 方法第 140 行逻辑，未注册工具直接跳过 DENY 检查，进入速率限制和参数检查后直接放行。
- **修复建议**：默认权限应设为 `PermissionLevel.DENY` 或 `RESTRICT`，实现白名单模式。

---

## 🟡 警告问题

### 4. 审计日志事件计数器竞态条件
- **文件**：`src/audit_logger.py` **第 163 行**
- **问题**：`self._event_counter += 1` 不是原子操作，在并发请求中可能导致事件 ID 重复。
- **修复建议**：使用 `threading.Lock` 保护计数器，或使用 `itertools.count()`。

### 5. 工具调用历史竞态条件
- **文件**：`src/tool_guard.py` **第 94 行**
- **问题**：`self.call_history` 列表在 `_record_call()`（第 264 行）和 `_check_rate_limit()`（第 192-208 行）中被并发读写，无锁保护。
- **修复建议**：使用 `threading.Lock` 保护 `call_history` 的读写操作。

### 6. 服务绑定 0.0.0.0
- **文件**：`src/web/app.py` **第 136 行**
- **问题**：`host="0.0.0.0"` 将服务暴露到所有网络接口。
- **修复建议**：默认绑定 `127.0.0.1`。

### 7. 审批队列逻辑未完整实现
- **文件**：`src/tool_guard.py` **第 97 行**
- **问题**：`self.approval_queue` 被初始化，`approve_call()` 方法存在，但 `check()` 方法中需要审批的工具调用仅返回 `allowed=False`，并未将调用加入审批队列。
- **修复建议**：在 `check()` 中将需要审批的调用添加到 `approval_queue`。

### 8. 危险内容检测模式过于简单
- **文件**：`src/tool_guard.py` **第 247-256 行**
- **问题**：`_contains_dangerous_content()` 仅检测 4 种模式（rm -rf、DROP TABLE、script、sudo），容易被大小写变体、编码绕过等方式规避。
- **修复建议**：扩展危险模式库；使用更健壮的检测方案（如正则的 Unicode 变体匹配）。

### 9. sys.path 操作方式不规范
- **文件**：`src/web/app.py` **第 11 行**，`src/macos/app.py` **第 13 行**，`examples/guardrail_demo.py` **第 10 行**
- **问题**：多处 `sys.path.insert(0, ...)` 修改模块搜索路径。
- **修复建议**：使用 `pyproject.toml` + `pip install -e .` 可编辑安装。

### 10. Web API 中 check_tool 调用错误方法名
- **文件**：`src/web/app.py` **第 97 行**
- **问题**：`result = guardrails.check_tool(req.tool_name, req.params)` 但 `Guardrails` 类实际方法名为 `check_tool_call()`。
- **修复建议**：改为 `guardrails.check_tool_call(req.tool_name, req.params)`。

---

## 🔵 建议

### 11. 输出过滤器的有害关键词集合有重复
- **文件**：`src/output_filter.py` **第 81-84 行**
- **问题**：`harmful_keywords` 集合中 `"暴力"` 出现两次（Python set 自动去重，但代码可读性差）。
- **修复建议**：去除重复项。

### 12. 缺少日志系统
- **问题**：安全防护系统应有完善的日志记录，当前仅 `AuditLogger` 有内存日志，但无持久化输出。
- **修复建议**：将审计日志持久化到文件或外部系统；核心模块使用 `logging` 模块。

### 13. 缺少测试用例
- **问题**：安全防护系统应有全面的测试覆盖，当前无单元测试。
- **修复建议**：为输入过滤、输出过滤、工具防护添加 pytest 测试，包括各种攻击向量的测试。

### 14. 依赖版本未锁定
- **文件**：`requirements.txt`
- **问题**：使用 `>=` 范围指定版本。
- **修复建议**：使用锁定文件固定版本。

### 15. InputFilter 敏感词检测可能误报
- **文件**：`src/input_filter.py` **第 168-180 行**
- **问题**：`"token"` 等敏感词在技术讨论中频繁出现（如 "access token"、"tokenizer"），会导致大量误报。
- **修复建议**：使用上下文相关的检测而非简单子串匹配；支持配置灵敏度级别。

---

## 总结评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 🔒 安全 | **5/10** | 安全防护系统本身缺少认证，CORS 全开，默认 ALLOW 危险 |
| 📊 质量 | **7/10** | 模块化设计良好，有完整的防护链路，但存在竞态和 API 调用错误 |
| 🏗️ 架构 | **8/10** | 四层防护（输入→输出→工具→审计）设计清晰，策略模式合理 |
