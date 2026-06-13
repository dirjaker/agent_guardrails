"""
Agent Guardrails macOS GUI
==========================
tkinter 桌面应用，提供安全防护功能的图形界面
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 确保能导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.guardrails import create_guardrails


class GuardrailsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Guardrails - 安全防护系统")
        self.root.geometry("800x600")
        self.root.configure(bg="#0d1117")

        self.guardrails = create_guardrails()
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#0d1117")
        style.configure("TNotebook.Tab", background="#161b22", foreground="#c9d1d9", padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", "#58a6ff")], foreground=[("selected", "#fff")])
        style.configure("TFrame", background="#0d1117")
        style.configure("TLabel", background="#0d1117", foreground="#c9d1d9")
        style.configure("TButton", background="#238636", foreground="#fff")
        style.map("TButton", background=[("active", "#2ea043")])

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # 输入检查 Tab
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="输入检查")
        ttk.Label(input_frame, text="输入待检查文本:").pack(anchor=tk.W, padx=8, pady=(8, 2))
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, bg="#0d1117", fg="#c9d1d9",
                                                      insertbackground="#c9d1d9", font=("Menlo", 12))
        self.input_text.pack(fill=tk.X, padx=8)
        ttk.Button(input_frame, text="执行检查", command=self.check_input).pack(anchor=tk.W, padx=8, pady=6)
        self.input_result = scrolledtext.ScrolledText(input_frame, height=8, bg="#161b22", fg="#c9d1d9",
                                                       font=("Menlo", 11), state=tk.DISABLED)
        self.input_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # 输出脱敏 Tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="输出脱敏")
        ttk.Label(output_frame, text="输入待脱敏文本:").pack(anchor=tk.W, padx=8, pady=(8, 2))
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, bg="#0d1117", fg="#c9d1d9",
                                                       insertbackground="#c9d1d9", font=("Menlo", 12))
        self.output_text.pack(fill=tk.X, padx=8)
        ttk.Button(output_frame, text="执行脱敏", command=self.check_output).pack(anchor=tk.W, padx=8, pady=6)
        self.output_result = scrolledtext.ScrolledText(output_frame, height=8, bg="#161b22", fg="#c9d1d9",
                                                        font=("Menlo", 11), state=tk.DISABLED)
        self.output_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # 工具检查 Tab
        tool_frame = ttk.Frame(notebook)
        notebook.add(tool_frame, text="工具检查")
        ttk.Label(tool_frame, text="工具名称:").pack(anchor=tk.W, padx=8, pady=(8, 2))
        self.tool_name = tk.Entry(tool_frame, bg="#0d1117", fg="#c9d1d9", insertbackground="#c9d1d9",
                                   font=("Menlo", 12))
        self.tool_name.pack(fill=tk.X, padx=8)
        ttk.Label(tool_frame, text="参数 (JSON):").pack(anchor=tk.W, padx=8, pady=(8, 2))
        self.tool_params = tk.Entry(tool_frame, bg="#0d1117", fg="#c9d1d9", insertbackground="#c9d1d9",
                                     font=("Menlo", 12))
        self.tool_params.pack(fill=tk.X, padx=8)
        ttk.Button(tool_frame, text="执行检查", command=self.check_tool).pack(anchor=tk.W, padx=8, pady=6)
        self.tool_result = scrolledtext.ScrolledText(tool_frame, height=8, bg="#161b22", fg="#c9d1d9",
                                                      font=("Menlo", 11), state=tk.DISABLED)
        self.tool_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _set_result(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def check_input(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return
        result = self.guardrails.check_input(text)
        lines = [f"Pass: {result.passed}", f"Action: {result.action.value}"]
        if result.warnings:
            lines.append(f"Warnings: {', '.join(result.warnings)}")
        if result.errors:
            lines.append(f"Errors: {', '.join(result.errors)}")
        self._set_result(self.input_result, "\n".join(lines))

    def check_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            return
        result = self.guardrails.check_output(text)
        filtered = text
        if result.output_result and hasattr(result.output_result, "filtered_output"):
            filtered = result.output_result.filtered_output or text
        lines = [f"Pass: {result.passed}", f"Action: {result.action.value}", f"Filtered: {filtered}"]
        if result.warnings:
            lines.append(f"Warnings: {', '.join(result.warnings)}")
        self._set_result(self.output_result, "\n".join(lines))

    def check_tool(self):
        name = self.tool_name.get().strip()
        if not name:
            return
        import json
        params = {}
        try:
            params = json.loads(self.tool_params.get() or "{}")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "参数格式错误，请输入有效 JSON")
            return
        result = self.guardrails.check_tool(name, params)
        allowed = True
        reason = ""
        if result.tool_result and hasattr(result.tool_result, "allowed"):
            allowed = result.tool_result.allowed
            reason = getattr(result.tool_result, "reason", "")
        lines = [f"Pass: {result.passed}", f"Allowed: {allowed}", f"Reason: {reason}"]
        self._set_result(self.tool_result, "\n".join(lines))


def main():
    root = tk.Tk()
    GuardrailsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
