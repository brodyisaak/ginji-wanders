#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from openai import OpenAI
TOOL_COLOR, OK_COLOR, ERR_COLOR, RESET = "\033[95m", "\033[2m", "\033[91m", "\033[0m"
DEFAULT_SYSTEM_PROMPT = (
    "you are ginji, a practical and careful coding agent. stay coding-focused, "
    "keep prose lowercase, and be honest about uncertainty. use tools when needed, "
    "avoid risky assumptions, and explain tradeoffs briefly."
)
def bash_exec(command: str) -> str:
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"error: failed to run command: {e}"
def read_file(path: str) -> str:
    try:
        p = Path(path)
        if not p.exists():
            return f"error: file not found: {path}"
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"error: failed to read file: {e}"
def write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"ok: wrote {path}"
    except Exception as e:
        return f"error: failed to write file: {e}"
def edit_file(path: str, old_str: str, new_str: str) -> str:
    current = read_file(path)
    if current.startswith("error:"):
        return current
    if old_str not in current:
        return "error: old_str not found in file"
    return write_file(path, current.replace(old_str, new_str, 1))
def list_files(directory: str = ".") -> str:
    try:
        root = Path(directory)
        if not root.exists():
            return f"error: directory not found: {directory}"
        files = [str((Path(dp) / n).relative_to(root)) for dp, _, names in os.walk(root) for n in names]
        return "\n".join(sorted(files))
    except Exception as e:
        return f"error: failed to list files: {e}"
def search_files(pattern: str, directory: str = ".") -> str:
    try:
        root = Path(directory)
        if not root.exists():
            return f"error: directory not found: {directory}"
        try:
            rx = re.compile(pattern)
        except re.error:
            rx = re.compile(re.escape(pattern))
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
TOOL_MAP = {"bash_exec": bash_exec, "read_file": read_file, "write_file": write_file, "edit_file": edit_file, "list_files": list_files, "search_files": search_files}
def tool_schema(name: str, props: dict, required=None) -> dict:
    return {"type": "function", "name": name, "description": f"call {name}", "parameters": {"type": "object", "properties": props, "required": required or [], "additionalProperties": False}}
TOOLS = [
    tool_schema("bash_exec", {"command": {"type": "string"}}, ["command"]),
    tool_schema("read_file", {"path": {"type": "string"}}, ["path"]),
    tool_schema("write_file", {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
    tool_schema("edit_file", {"path": {"type": "string"}, "old_str": {"type": "string"}, "new_str": {"type": "string"}}, ["path", "old_str", "new_str"]),
    tool_schema("list_files", {"directory": {"type": "string"}}),
    tool_schema("search_files", {"pattern": {"type": "string"}, "directory": {"type": "string"}}, ["pattern"]),
]
def load_skills(skills_dir: str) -> str:
    root = Path(skills_dir)
    if not root.exists():
        return ""
    blocks = []
    for path in sorted(root.rglob("SKILL.md")):
        text = read_file(str(path))
        if not text.startswith("error:"):
            blocks.append(f"skill file: {path}\n\n{text.strip()}")
    return "\n\n".join(blocks)
def execute_tool(name: str, raw_args: str) -> str:
    fn = TOOL_MAP.get(name)
    if not fn:
        return f"error: unknown tool: {name}"
    try:
        args = json.loads(raw_args or "{}")
        if not isinstance(args, dict):
            return "error: malformed tool arguments: expected object"
    except Exception as e:
        return f"error: malformed tool arguments: {e}"
    try:
        return str(fn(**args))
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"
    except Exception as e:
        return f"error: tool failed: {e}"
def extract_text(response) -> str:
    if getattr(response, "output_text", ""):
        return response.output_text
    parts = []
    for item in getattr(response, "output", []):
        if getattr(item, "type", "") == "message":
            parts.extend([c.text for c in getattr(item, "content", []) if hasattr(c, "text")])
    return "\n".join([p for p in parts if p]).strip()
def print_usage(response) -> None:
    usage = getattr(response, "usage", None)
    if not usage:
        return
    getv = lambda o, k: o.get(k) if isinstance(o, dict) else getattr(o, k, None)
    itok, otok, ttok = getv(usage, "input_tokens"), getv(usage, "output_tokens"), getv(usage, "total_tokens")
    if any(v is not None for v in [itok, otok, ttok]):
        print(f"tokens: input={itok} output={otok} total={ttok}")
def run_task(task: str, model: str, system_prompt: str) -> None:
    client = OpenAI()
    response = client.responses.create(model=model, input=[{"role": "system", "content": system_prompt}, {"role": "user", "content": task}], tools=TOOLS)
    while True:
        calls = [x for x in getattr(response, "output", []) if getattr(x, "type", "") == "function_call"]
        if not calls:
            break
        outputs = []
        for call in calls:
            name = getattr(call, "name", "unknown")
            print(f"{TOOL_COLOR}tool {name}{RESET}")
            result = execute_tool(name, getattr(call, "arguments", "{}"))
            print(f"{ERR_COLOR if result.startswith('error:') else OK_COLOR}{result[:300]}{RESET}")
            outputs.append({"type": "function_call_output", "call_id": getattr(call, "call_id", ""), "output": result})
        response = client.responses.create(model=model, input=outputs, tools=TOOLS, previous_response_id=response.id)
    print(extract_text(response))
    print_usage(response)
def build_system_prompt(args) -> str:
    parts = [DEFAULT_SYSTEM_PROMPT]
    if args.system_file:
        parts.append(read_file(args.system_file))
    if args.system:
        parts.append(args.system)
    if args.skills:
        skills = load_skills(args.skills)
        if skills:
            parts.insert(0, skills)
    return "\n\n".join([p for p in parts if p.strip()])
def main() -> None:
    p = argparse.ArgumentParser(description="ginji")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--prompt", "-p")
    p.add_argument("--system")
    p.add_argument("--system-file")
    p.add_argument("--skills")
    args = p.parse_args()
    system_prompt = build_system_prompt(args)
    piped = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    prompt = piped or (args.prompt or "")
    if prompt:
        run_task(prompt, args.model, system_prompt)
        return
    while True:
        try:
            text = input("ginji> ").strip()
        except EOFError:
            print()
            return
        if text in {"exit", "quit"}:
            return
        if text:
            try:
                run_task(text, args.model, system_prompt)
            except Exception as e:
                print(f"error: {e}")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ninterrupted.")
