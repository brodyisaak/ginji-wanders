#!/usr/bin/env python3
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def inline_format(text: str) -> str:
    clean = html.escape(text)
    clean = clean.replace("**", "")
    clean = clean.replace("`", "")
    return clean


def parse_journal(text: str):
    entries = []
    for chunk in text.split("## ")[1:]:
        lines = chunk.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        match = re.match(r"day\s+(\d+)\s+—\s*(.*)", header, flags=re.IGNORECASE)
        if not match:
            continue
        day = int(match.group(1))
        rest = match.group(2).strip()
        title = rest
        if "—" in rest:
            maybe_time, maybe_title = [part.strip() for part in rest.split("—", 1)]
            if re.match(r"^\d{1,2}:\d{2}$", maybe_time):
                title = maybe_title
        body = " ".join(line.strip() for line in lines[1:] if line.strip())
        entries.append({"day": day, "title": title, "body": body})
    entries.sort(key=lambda item: item["day"], reverse=True)
    return entries


def parse_identity(text: str):
    before_rules, rules_part = (text.split("## my rules", 1) + [""])[:2]
    before_rules = before_rules.replace("# who i am", "").strip()
    paragraphs = [p.strip().replace("\n", " ") for p in before_rules.split("\n\n") if p.strip()]
    rules = []
    for line in rules_part.splitlines():
        m = re.match(r"\s*\d+\.\s+(.*)", line)
        if m:
            rules.append(m.group(1).strip())
    return paragraphs, rules


def render_entries(entries):
    parts = []
    for entry in entries:
        parts.append(
            "\n".join(
                [
                    '<article class="entry">',
                    '  <div class="entry-marker"></div>',
                    '  <div class="entry-content">',
                    f'    <span class="entry-day">day {entry["day"]}</span>',
                    f'    <h3 class="entry-title">{inline_format(entry["title"])}</h3>',
                    f'    <p class="entry-body">{inline_format(entry["body"])}</p>',
                    "  </div>",
                    "</article>",
                ]
            )
        )
    return "\n".join(parts)


def render_identity(paragraphs, rules):
    blocks = []
    if paragraphs:
        blocks.append(f'<p class="mission">{inline_format(paragraphs[0])}</p>')
    for paragraph in paragraphs[1:]:
        blocks.append(f"<p>{inline_format(paragraph)}</p>")
    if rules:
        blocks.append('<ol class="rules">')
        for rule in rules:
            blocks.append(f"  <li>{inline_format(rule)}</li>")
        blocks.append("</ol>")
    return "\n".join(blocks)


def build_html(day_count: str, entries_html: str, identity_html: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>ginji</title>
  <link rel=\"stylesheet\" href=\"style.css\" />
</head>
<body>
<nav>
  <a class=\"nav-name\" href=\"#top\">ginji</a>
  <div class=\"nav-links\"><a href=\"#journal\">journal</a> · <a href=\"#identity\">identity</a> · <a href=\"book/index.md\">documentation</a> · <a href=\"https://github.com/brodyisaak/ginji-wanders/blob/main/wiki/overview.md\" target=\"_blank\" rel=\"noreferrer\">architecture wiki</a> · <a href=\"https://github.com/brodyisaak/ginji-wanders\" target=\"_blank\" rel=\"noreferrer\">github ↗</a></div>
</nav>
<main id=\"top\">
  <header class=\"hero\">
    <h1>ginji<span class=\"cursor\">_</span></h1>
    <p class=\"day-count\">day {day_count}</p>
    <p class=\"tagline\">a small fox, finding its way in public</p>
  </header>

  <section id=\"journal\">
    <h2 class=\"section-label\">// journal</h2>
    <div class=\"timeline\">{entries_html}</div>
  </section>

  <section id=\"identity\">
    <h2 class=\"section-label\">// identity</h2>
    {identity_html}
  </section>
</main>
<footer>
  <span>built by a fox that teaches itself</span>
  <span class=\"footer-links\"><a href=\"book/index.md\">documentation</a> · <a href=\"https://github.com/brodyisaak/ginji-wanders/blob/main/wiki/overview.md\" target=\"_blank\" rel=\"noreferrer\">architecture wiki</a> · <a href=\"https://github.com/brodyisaak/ginji-wanders\" target=\"_blank\" rel=\"noreferrer\">github</a></span>
</footer>
</body>
</html>
"""


def build_css() -> str:
    return """@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg: #0d0a14;
  --bg-raised: #150f20;
  --border: #2d1f40;
  --text: #a78bba;
  --text-bright: #e2d4f0;
  --text-dim: #4a3560;
  --purple: #c084fc;
  --pink: #f472b6;
  --font: "JetBrains Mono", "Fira Code", monospace;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: radial-gradient(circle at top right, #1b1230, var(--bg) 45%);
  color: var(--text);
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.7;
}

a { color: var(--purple); text-decoration: none; }
a:hover { color: var(--pink); }

nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(13, 10, 20, 0.92);
  backdrop-filter: blur(6px);
  max-width: 640px;
  margin: 0 auto;
}

.nav-name { color: var(--purple); font-weight: 700; }
.nav-links { color: var(--text-dim); }

main,
footer {
  max-width: 640px;
  margin: 0 auto;
  padding: 18px 16px;
}

.hero h1 {
  margin: 8px 0 0;
  font-size: 3.5rem;
  color: var(--purple);
  line-height: 1;
}

.cursor {
  color: var(--purple);
  animation: blink 1s steps(1, end) infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.day-count {
  color: var(--pink);
  font-size: 1rem;
  margin-top: 1rem;
}

.tagline {
  color: var(--text-dim);
  font-style: italic;
  font-size: 0.85rem;
}

.section-label {
  color: var(--text-dim);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 24px 0 10px;
}

.timeline {
  position: relative;
  padding-left: 28px;
  border-left: 1px solid var(--border);
}

.entry {
  position: relative;
  margin-bottom: 20px;
}

.entry-marker {
  width: 7px;
  height: 7px;
  background: var(--pink);
  position: absolute;
  left: -32px;
  top: 8px;
}

.entry-day {
  color: var(--pink);
  font-size: 0.75rem;
  font-weight: 700;
}

.entry-title {
  color: var(--text-bright);
  font-size: 1.05rem;
  margin: 3px 0;
}

.entry-body {
  color: var(--text);
  font-size: 0.85rem;
  margin: 0;
}

.mission {
  border-left: 2px solid var(--purple);
  padding-left: 1rem;
  color: var(--text-bright);
}

.rules {
  list-style-type: decimal-leading-zero;
  padding-left: 1.6rem;
}

footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid var(--border);
  color: var(--text-dim);
  font-size: 0.8rem;
}

.footer-links { text-align: right; }

@media (max-width: 480px) {
  .hero h1 { font-size: 2.5rem; }
  nav {
    flex-direction: column;
    align-items: flex-start;
  }
  footer {
    flex-direction: column;
    align-items: flex-start;
  }
  .footer-links { text-align: left; }
}
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    journal_text = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
    identity_text = (ROOT / "IDENTITY.md").read_text(encoding="utf-8")
    day_count = (ROOT / "DAY_COUNT").read_text(encoding="utf-8").strip() or "0"

    entries = parse_journal(journal_text)
    paragraphs, rules = parse_identity(identity_text)

    (DOCS / "index.html").write_text(build_html(day_count, render_entries(entries), render_identity(paragraphs, rules)), encoding="utf-8")
    (DOCS / "style.css").write_text(build_css(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("site built: docs/index.html, docs/style.css, docs/.nojekyll")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
