---
name: site-ux-audit
description: review the generated site on desktop and mobile for navigation clarity, hierarchy, stats usability, journal browsing, footer polish, and interaction quality
tools: [bash_exec, read_file, write_file]
---

# site ux audit

this skill is for reviewing the site before or after design changes.

the main goal is not to ask "does it look nice?" but "does it feel clear, intentional, and easy to use?"

## audit surfaces

- nav
- hero
- stats strip
- journal timeline
- show more control
- footer
- desktop layout
- mobile layout

## audit workflow

1. read `scripts/build_site.py` to understand what the generator intends.
2. rebuild the site with `python3 scripts/build_site.py`.
3. review the generated `docs/index.html` and `docs/style.css`.
4. inspect both desktop and mobile behavior.
5. write findings in priority order: first impression, clarity, readability, then polish.

## desktop checks

- does the nav feel compact, clear, and intentionally placed?
- is the hero strong without feeling oversized?
- do the stats help explain progress quickly?
- is the timeline easy to scan?
- does the footer feel connected to the rest of the system?

## mobile checks

- is the nav simpler than desktop without becoming awkward?
- does the top of the page avoid wasting height?
- do cards scale down cleanly?
- is the journal still readable without huge blocks?
- can someone browse quickly with one hand?

## common failure modes

- nav takes too much vertical space
- mobile behavior feels like a desktop pattern forced into a smaller viewport
- stats become oversized boxes instead of quick signals
- latest entry feels visually heavier than the rest of the page
- contrast is technically strong but emotionally harsh
- buttons look unrelated to the rest of the ui

## output format

write findings as:

1. [high/medium/low] issue
2. why it hurts the experience
3. the smallest good fix

prefer statements like:
- "mobile nav uses too much height for only five links"
- "stats cards read as containers, not signals"
- "timeline density drops too hard after the first screen"

avoid vague comments like:
- "looks weird"
- "not modern enough"

## decision rules

- if desktop is already working, do not destabilize it just to fix mobile.
- if mobile is awkward, prefer changing layout logic over adding another control.
- if a component needs explanation to feel good, it is probably too complicated.

