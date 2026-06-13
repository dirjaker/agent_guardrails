"""
Agent Guardrails Web API
========================
FastAPI 服务，暴露安全防护功能的 REST 接口
"""

import sys
import os

# 确保能导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from src.guardrails import create_guardrails, Guardrails, GuardrailConfig

app = FastAPI(title="Agent Guardrails API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 挂载静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 全局实例
guardrails = create_guardrails()


class InputCheckRequest(BaseModel):
    text: str
    user_id: str = ""


class OutputCheckRequest(BaseModel):
    text: str


class ToolCheckRequest(BaseModel):
    tool_name: str
    params: dict = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回仪表盘页面"""
    html_path = os.path.join(static_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/api/check/input")
async def check_input(req: InputCheckRequest):
    """检查用户输入的安全性"""
    result = guardrails.check_input(req.text, req.user_id)
    return {
        "passed": result.passed,
        "action": result.action.value,
        "warnings": result.warnings,
        "errors": result.errors,
        "threats": [
            {"type": t.threat_type.value, "detail": t.detail, "severity": t.severity}
            for t in result.input_result.threats
        ] if result.input_result and hasattr(result.input_result, "threats") else []
    }


@app.post("/api/check/output")
async def check_output(req: OutputCheckRequest):
    """检查并脱敏输出内容"""
    result = guardrails.check_output(req.text)
    filtered = ""
    if result.output_result and hasattr(result.output_result, "filtered_output"):
        filtered = result.output_result.filtered_output
    return {
        "passed": result.passed,
        "action": result.action.value,
        "original": req.text,
        "filtered": filtered or req.text,
        "warnings": result.warnings,
        "errors": result.errors
    }


@app.post("/api/check/tool")
async def check_tool(req: ToolCheckRequest):
    """检查工具调用是否被允许"""
    result = guardrails.check_tool(req.tool_name, req.params)
    allowed = True
    reason = ""
    if result.tool_result and hasattr(result.tool_result, "allowed"):
        allowed = result.tool_result.allowed
        reason = getattr(result.tool_result, "reason", "")
    return {
        "passed": result.passed,
        "allowed": allowed,
        "reason": reason,
        "tool": req.tool_name,
        "warnings": result.warnings,
        "errors": result.errors
    }


@app.get("/api/audit/stats")
async def audit_stats():
    """获取审计统计信息"""
    if guardrails.audit_logger:
        stats = guardrails.audit_logger.get_stats()
        return stats if isinstance(stats, dict) else {"stats": str(stats)}
    return {"message": "审计日志未启用"}


@app.get("/api/config")
async def get_config():
    """获取当前防护配置"""
    return {
        "input_filter": guardrails.config.enable_input_filter,
        "output_filter": guardrails.config.enable_output_filter,
        "tool_guard": guardrails.config.enable_tool_guard,
        "audit_log": guardrails.config.enable_audit_log,
        "strict_mode": guardrails.config.strict_mode
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
