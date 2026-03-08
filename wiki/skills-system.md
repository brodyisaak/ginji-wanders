# skills system

## representation

a skill is a `SKILL.md` file with yaml frontmatter and markdown instructions.

## yaml frontmatter

supported fields:
- `name`
- `description`
- `tools`

## parsing and concatenation

ginji reads each skill file, parses frontmatter, keeps instruction body, and concatenates all discovered skills into a single prepended system-context block.

## why this matters

skills constrain and guide autonomous changes so evolution stays aligned with mission, safety rules, and repo conventions.
