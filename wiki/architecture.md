# architecture

## purpose

this page documents the runtime decomposition and why ginji stays intentionally small.

## system boundaries

primary runtime units:
- cli and repl orchestration
- prompt composition
- tool contract definitions
- tool execution loop
- usage reporting

supporting units:
- protected autonomous kernel
- mutable autonomous runtime
- static site builder
- workflow automation

## component map

1. `src/ginji.py`
   - parses cli flags
   - builds system prompt
   - defines tool schema and dispatch map
   - runs openai tool-call loop
2. `scripts/evolve.sh`
   - enforces the protected outer rails: env checks, pacific day guard, journal preservation, final build gate, commit, tag, and push
3. `scripts/evolve_runtime.py`
   - runs planning, metric selection, bounded iterations, issue response handling, learnings, and site rebuild
4. `scripts/build_site.py`
   - renders docs site from state files
5. `tests/test_ginji.py`
   - validates local tool behavior

## step-by-step flow

1. parse runtime inputs and determine execution mode.
2. load optional skills and merge prompt layers.
3. call openai api with available function tools.
4. execute tools with local filesystem and shell access.
5. append tool outputs back into conversation state.
6. continue until model returns no tool calls.
7. print final response and optional token usage.

## design constraints

- functional style over class hierarchy.
- all tool results return strings, including errors.
- normal tool failures should not crash repl.
- minimal dependencies: openai sdk and pytest.

## what can go wrong

- malformed tool json can break dispatch if not guarded.
- tool functions may diverge from tests.
- prompt layer ordering can become inconsistent.
- mutable harness logic can drift unless the kernel/runtime boundary stays explicit.

## diagnostics

```bash
rg -n "def (bash_exec|read_file|write_file|edit_file|list_files|search_files)" src/ginji.py
rg -n "--skills|system prompt|tool" src/ginji.py
python -m pytest tests/test_ginji.py -v
```

## recovery actions

- restore contract behavior by aligning tool implementations with test expectations.
- if prompt composition regresses, compare against known-good commit and update tests.
- if evolution behavior regresses, check whether the change belonged in `scripts/evolve_runtime.py` instead of the protected kernel.

## how to verify

- every tool function is importable and tested.
- repl mode still runs with no prompt argument.
- piped input still executes single-shot tasks.

## related pages

- [runtime loop and message flow](./runtime-loop-and-message-flow.md)
- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [testing and safety](./testing-and-safety.md)
