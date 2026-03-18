---
name: site-design
description: improve the visual system of the generated site with stronger hierarchy, spacing, typography, color restraint, and component consistency
tools: [bash_exec, read_file, write_file, edit_file]
---

# site design

this skill governs visual-system work for ginji's public site.

the main surfaces are:
- `scripts/build_site.py`
- `docs/index.html`
- `docs/style.css`

## goal

make the site feel more expressive and memorable without losing its calm technical honesty.

the target mood is:
- refined terminal
- muted purple and pink, not neon overload
- clear hierarchy
- strong first impression
- readable on desktop and mobile

## default approach

1. read `scripts/build_site.py` and identify which html structure is generated versus which styles are purely css.
2. inspect `docs/index.html` only as generated output, not the main source of truth.
3. treat `docs/style.css` as the visual system layer.
4. make a small number of coordinated changes instead of many unrelated tweaks.
5. rebuild the site after each meaningful pass with `python3 scripts/build_site.py`.

## visual system rules

### hierarchy
- hero, nav, stats, timeline, and footer should each have a distinct role.
- the eye should land on `ginji`, then the current day, then the latest progress signal.
- labels should be quieter than values.
- system chrome should not compete with journal content.

### spacing
- use a consistent spacing rhythm across nav, hero, cards, timeline, and footer.
- reduce wasted vertical space before adding more color or decoration.
- mobile spacing should be tighter than desktop, but never cramped.

### typography
- keep the site grounded in a technical voice.
- mono can remain the core system font, but hierarchy must still be clear through scale, weight, letter spacing, and contrast.
- if a second font is introduced, use it sparingly and only for display moments.

### component consistency
- repeated controls should feel related.
- nav, pills, cards, timeline markers, and footer controls should share a visual language.
- avoid one-off shapes or shadows that do not appear elsewhere.

### color restraint
- keep purple and pink as identity accents, but mute them when they overpower readability.
- use bright accent color for focus moments, not every surface.
- prefer subtle contrast shifts over adding more saturated colors.

## what good looks like

- the nav feels intentional, not generic.
- the hero feels like a product and a journal at the same time.
- the stats support the story instead of stealing attention.
- the journal timeline is easy to scan quickly.
- the footer feels finished, not leftover.
- mobile keeps the same identity as desktop, just denser and simpler.

## what to avoid

- random visual experiments without a system reason
- excessive glow, blur, or glass
- high-saturation pink and purple everywhere
- overly tall mobile sections
- controls that behave one way on desktop and awkwardly on mobile
- decorative changes that reduce readability

## before finishing

1. rebuild with `python3 scripts/build_site.py`
2. check desktop and mobile layout
3. verify that the current journal still reads clearly
4. make sure the site still feels like ginji, not a generic startup template

