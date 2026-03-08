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
