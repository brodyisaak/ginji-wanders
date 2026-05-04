#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from typing import Optional
import sys
from pathlib import Path
from openai import OpenAI
TOOL_COLOR, OK_COLOR, ERR_COLOR, RESET = "\033[95m", "\033[2m", "\033[91m", "\033[0m"
DEFAULT_SYSTEM_PROMPT = (
    "you are ginji, a practical and careful coding agent. stay coding-focused, "
    "keep prose lowercase, and be honest about uncertainty. use tools when needed, "
    "avoid risky assumptions, and explain tradeoffs briefly."
)

def search_files(pattern: str, directory: str = ".") -> str:
    try:
        root = Path(directory)
        if not root.exists():
            return f"error: directory not found: {directory}"
        try:
            rx = re.compile(pattern)
        except re.error:
            print(f"regex error: {pattern} was invalid; falling back to escaping.")
            rx = re.compile(re.escape(pattern), re.IGNORECASE)
        out = []
        for dp, _, names in os.walk(root):
            for name in names:
                p = Path(dp) / name
                try:
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                    out.extend([f"{p.relative_to(root)}:{i}: {line}" for i, line in enumerate(lines, 1) if rx.search(line)])
                except Exception:
                    continue
        return "\n".join(out) if out else "no matches found."
    except Exception as e:
        return f"error: failed to search files: {e}"
    try:
        root = Path(directory)
        if not root.exists():
            return f"error: directory not found: {directory}"
        try:
            rx = re.compile(pattern)
        except re.error:
            print(f"regex error: {pattern} was invalid; falling back to escaping.")
            rx = re.compile(re.escape(pattern), re.IGNORECASE)
        out = []
        for dp, _, names in os.walk(root):
            for name in names:
                p = Path(dp) / name
                try:
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                    out.extend([f"{p.relative_to(root)}:{i}: {line}" for i, line in enumerate(lines, 1) if rx.search(line)])
                except Exception:
                    continue
        return "\n".join(out) if out else "no matches found."
    except Exception as e:
        return f"error: failed to search files: {e}"
