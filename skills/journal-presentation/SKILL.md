---
name: journal-presentation
description: improve how the journal is presented on the site through better timeline density, excerpt handling, browsing rhythm, and show more behavior
tools: [bash_exec, read_file, write_file, edit_file]
---

# journal presentation

the journal is the heart of the site. treat it like the main product surface, not a leftover content block.

the journal should feel:
- alive
- easy to scan
- honest
- lightweight to browse

## source of truth

- `JOURNAL.md` is the content source
- `scripts/build_site.py` controls how entries are parsed and rendered
- `docs/style.css` controls density, hierarchy, and browsing rhythm

## presentation goals

1. newest entry should feel present, but not so dominant that older entries disappear.
2. titles should be easy to skim.
3. body excerpts should provide enough signal without becoming walls of text.
4. the timeline should keep visual rhythm as the archive grows.
5. the `show more` control should feel native to the rest of the ui.

## timeline rules

- markers should guide the eye, not distract from reading.
- spacing between entries should feel even and predictable.
- the line, marker, day label, title, and body should read as one unit.
- dense enough to browse, loose enough to breathe.

## excerpt rules

- do not let long entries dominate mobile.
- preserve the voice of the journal, but trim or style for scanability when needed.
- if truncation is used, it should feel intentional and reversible.
- avoid visual dead space caused by mismatched card heights or oversized excerpts.

## show more rules

- `show more` should reveal archive content without feeling like a jarring mode switch.
- if there is a paired collapse behavior, it should return the reader to a stable place.
- button language and styling should match the rest of the site controls.
- count labels should stay accurate.

## what to avoid

- making the journal secondary to the hero or stats
- entries that look identical regardless of importance or recency
- giant mobile excerpts with too much empty space
- archive controls that feel bolted on
- timeline spacing that changes unpredictably across breakpoints

## finishing check

after changes:
1. rebuild with `python3 scripts/build_site.py`
2. verify newest entry, older entries, and hidden entries all render correctly
3. test journal browsing on mobile and desktop
4. make sure the page still feels like a public memory, not a blog template

