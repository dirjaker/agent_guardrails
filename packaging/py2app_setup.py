"""
py2app 打包脚本 - Agent Guardrails
===================================
使用方法:
    python packaging/py2app_setup.py py2app
"""

from setuptools import setup

APP = ["src/macos/app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["src"],
    "includes": ["tkinter"],
    "excludes": ["matplotlib", "numpy", "scipy", "pandas"],
    "iconfile": None,
    "plist": {
        "CFBundleName": "Agent Guardrails",
        "CFBundleDisplayName": "Agent Guardrails",
        "CFBundleIdentifier": "com.dirjaker.agent-guardrails",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "MIT License",
    },
}

setup(
    name="Agent Guardrails",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
