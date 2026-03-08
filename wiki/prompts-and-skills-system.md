# prompts and skills system

## purpose

document how prompt layers are assembled and how skill files constrain autonomous behavior.

## system boundaries

prompt inputs:
- built-in default system prompt in runtime
- optional `--system` text
- optional `--system-file` content
- optional skills directory loaded via `--skills`

skill inputs:
- recursive `SKILL.md` discovery
- yaml frontmatter with `name`, `description`, `tools`
- markdown body instructions

## step-by-step flow

1. load built-in system prompt.
2. append explicit system overrides from flags.
3. discover all `SKILL.md` files recursively under selected skills path.
4. parse frontmatter and body for each skill file.
5. concatenate formatted skill blocks and prepend/append according to runtime strategy.
6. send final system context with user messages to openai api.

## precedence and guidance rules

- explicit operator context from cli should stay deterministic.
- skills provide operational policy and safety constraints.
- malformed skill frontmatter should not crash runtime.

## what can go wrong

- broken yaml blocks can silently skip critical constraints.
- duplicated skill instructions can conflict on priorities.
- very large skill payload can reduce model focus.

## diagnostics

```bash
rg -n "name:|description:|tools:" skills/**/SKILL.md
python src/ginji.py --skills skills -p "summarize active skills"
```

## recovery actions

- keep skill files small, focused, and explicit.
- if conflicts appear, consolidate rules into one authoritative skill.
- add tests for skill parsing edge cases when parser changes.

## how to verify

- runtime loads nested skill files, not just top-level directories.
- prompt output behavior changes when `--skills` is omitted vs included.
- no crash on missing or malformed optional skill file.

## related pages

- [runtime loop and message flow](./runtime-loop-and-message-flow.md)
- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)
