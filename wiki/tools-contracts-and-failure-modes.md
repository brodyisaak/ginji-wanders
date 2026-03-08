# tools contracts and failure modes

## purpose

define exact behavior contracts for ginji tool functions so changes stay compatible and testable.

## system boundaries

tools are module-level functions in `src/ginji.py`:
- `bash_exec(command: str) -> str`
- `read_file(path: str) -> str`
- `write_file(path: str, content: str) -> str`
- `edit_file(path: str, old_str: str, new_str: str) -> str`
- `list_files(directory: str = ".") -> str`
- `search_files(pattern: str, directory: str = ".") -> str`

## contract summary

- all tool outputs are strings.
- normal operational failures return error strings, not uncaught exceptions.
- filesystem tools operate relative to current working directory unless absolute path is provided.

## step-by-step tool behavior

1. parse tool args from model response json.
2. map function name to callable.
3. execute callable with provided arguments.
4. catch and stringify failures.
5. append output into conversation as tool result.

## common failure modes

- `bash_exec`: command not found, permissions denied, non-zero exit status.
- `read_file`: path missing or unreadable.
- `write_file`: invalid parent path or write permissions.
- `edit_file`: `old_str` not found in target content.
- `list_files`: directory missing.
- `search_files`: invalid regex or unreadable files.

## diagnostics

```bash
python -m pytest tests/test_ginji.py -v
python - <<'PY'
from src.ginji import edit_file
print(edit_file('missing.txt', 'a', 'b'))
PY
```

## recovery actions

- tighten error strings and keep them human-readable.
- add tests before changing any contract text or return shape.
- avoid introducing non-string return types.

## how to verify

- existing tool tests pass.
- manually trigger at least one error case per changed tool.
- confirm repl still prints tool execution feedback without crashing.

## related pages

- [runtime loop and message flow](./runtime-loop-and-message-flow.md)
- [testing and safety](./testing-and-safety.md)
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)
