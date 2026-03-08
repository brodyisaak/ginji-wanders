# skills

skills are markdown instruction files with yaml frontmatter that shape agent behavior.

ginji recursively discovers every `SKILL.md` under the configured skills directory and prepends skill content into the system prompt.

frontmatter fields:
- `name`
- `description`
- `tools`

bundled skills:
- `self-assess`
- `evolve`
- `communicate`

## deep wiki

- [prompts and skills system](../../wiki/prompts-and-skills-system.md)
- [contribution guidelines for agent safe changes](../../wiki/contribution-guidelines-for-agent-safe-changes.md)
