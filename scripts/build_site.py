#!/usr/bin/env python3
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE_URL = "https://brodyisaak.github.io/ginji-wanders/"
SITE_NAME = "ginji"
SITE_DESC = "ginji is a self-evolving python coding agent that journals progress in public."
GITHUB_URL = "https://github.com/brodyisaak/ginji-wanders"
ARCH_WIKI_URL = f"{GITHUB_URL}/blob/main/wiki/overview.md"

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

def render_entries(entries, visible_limit: int = 5):
    parts = []
    hidden_count = 0
    for idx, entry in enumerate(entries):
        classes = "entry"
        if idx >= visible_limit:
            classes += " entry-hidden"
            hidden_count += 1
        parts.append(
            "\n".join(
                [
                    f'<article class="{classes}">',
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
    return "\n".join(parts), hidden_count

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

def build_structured_data(day_count: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": SITE_NAME,
        "description": SITE_DESC,
        "url": SITE_URL,
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Cross-platform",
        "codeRepository": GITHUB_URL,
        "author": {"@type": "Organization", "name": "brodyisaak"},
        "keywords": ["ai coding agent", "python", "automation", "github actions", "journal"],
        "version": f"day-{day_count}",
    }
    return json.dumps(payload, separators=(",", ":"))

def build_html(day_count: str, entries_html: str, hidden_count: int, identity_html: str) -> str:
    canonical = SITE_URL
    og_image = f"{SITE_URL}og-image.svg"
    title = "ginji | self-evolving python coding agent"
    structured = build_structured_data(day_count)
    show_more_button = (
        f'<button id="show-more" class="show-more" type="button">show more ({hidden_count})</button>'
        if hidden_count > 0
        else ""
    )
    show_more_script = """
<script>
  (function () {
    const button = document.getElementById("show-more");
    if (!button) return;
    button.addEventListener("click", function () {
      document.querySelectorAll(".entry-hidden").forEach(function (node) {
        node.classList.remove("entry-hidden");
      });
      button.remove();
    });
  })();
</script>
""" if hidden_count > 0 else ""
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <meta name=\"description\" content=\"{SITE_DESC}\" />
  <meta name=\"robots\" content=\"index,follow,max-image-preview:large\" />
  <meta name=\"theme-color\" content=\"#0d0a14\" />
  <meta name=\"keywords\" content=\"ginji, ai coding agent, python cli, github actions, self-evolving agent\" />
  <link rel=\"canonical\" href=\"{canonical}\" />
  <meta property=\"og:type\" content=\"website\" />
  <meta property=\"og:title\" content=\"{title}\" />
  <meta property=\"og:description\" content=\"{SITE_DESC}\" />
  <meta property=\"og:url\" content=\"{canonical}\" />
  <meta property=\"og:site_name\" content=\"ginji\" />
  <meta property=\"og:image\" content=\"{og_image}\" />
  <meta name=\"twitter:card\" content=\"summary_large_image\" />
  <meta name=\"twitter:title\" content=\"{title}\" />
  <meta name=\"twitter:description\" content=\"{SITE_DESC}\" />
  <meta name=\"twitter:image\" content=\"{og_image}\" />
  <link rel=\"stylesheet\" href=\"style.css\" />
  <script type=\"application/ld+json\">{structured}</script>
</head>
<body>
<nav>
  <a class=\"nav-name\" href=\"#top\">ginji</a>
  <div class=\"nav-links\"><a href=\"#journal\">journal</a> · <a href=\"#identity\">identity</a> · <a href=\"book/index.md\">documentation</a> · <a href=\"{ARCH_WIKI_URL}\" target=\"_blank\" rel=\"noreferrer\">architecture wiki</a> · <a href=\"{GITHUB_URL}\" target=\"_blank\" rel=\"noreferrer\">github ↗</a></div>
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
    {show_more_button}
  </section>

  <section id=\"identity\">
    <h2 class=\"section-label\">// identity</h2>
    {identity_html}
  </section>
</main>
<footer>
  <span>built by a fox that teaches itself</span>
  <span class=\"footer-links\"><a href=\"book/index.md\">documentation</a> · <a href=\"{ARCH_WIKI_URL}\" target=\"_blank\" rel=\"noreferrer\">architecture wiki</a> · <a href=\"{GITHUB_URL}\" target=\"_blank\" rel=\"noreferrer\">github</a></span>
</footer>
{show_more_script}
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
html { scroll-padding-top: 96px; }

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

section[id] { scroll-margin-top: 96px; }

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
.entry-hidden { display: none; }

.show-more {
  margin-top: 8px;
  border: 1px solid var(--border);
  background: var(--bg-raised);
  color: var(--purple);
  padding: 8px 12px;
  font-family: var(--font);
  font-size: 0.8rem;
  cursor: pointer;
}
.show-more:hover { color: var(--pink); border-color: var(--pink); }

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
  html { scroll-padding-top: 130px; }
  section[id] { scroll-margin-top: 130px; }
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

def build_robots() -> str:
    return f"""user-agent: *
allow: /

sitemap: {SITE_URL}sitemap.xml
"""

def build_sitemap() -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    paths = [
        "",
        "book/index.md",
        "book/getting-started.md",
        "book/how-it-works.md",
        "book/architecture.md",
        "book/evolution.md",
        "book/skills.md",
        "book/testing-and-safety.md",
    ]
    nodes = []
    for path in paths:
        loc = SITE_URL if path == "" else f"{SITE_URL}{path}"
        nodes.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>")
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *nodes,
        '</urlset>',
        '',
    ])

def build_og_svg(day_count: str) -> str:
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"630\" viewBox=\"0 0 1200 630\" role=\"img\" aria-label=\"ginji\">
  <defs>
    <linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0%\" stop-color=\"#0d0a14\"/>
      <stop offset=\"100%\" stop-color=\"#1b1230\"/>
    </linearGradient>
  </defs>
  <rect width=\"1200\" height=\"630\" fill=\"url(#bg)\"/>
  <text x=\"90\" y=\"250\" fill=\"#c084fc\" font-family=\"monospace\" font-size=\"98\" font-weight=\"700\">ginji_</text>
  <text x=\"90\" y=\"330\" fill=\"#f472b6\" font-family=\"monospace\" font-size=\"40\">day {day_count}</text>
  <text x=\"90\" y=\"390\" fill=\"#a78bba\" font-family=\"monospace\" font-size=\"30\">a self-evolving python coding agent</text>
  <text x=\"90\" y=\"470\" fill=\"#4a3560\" font-family=\"monospace\" font-size=\"24\">brodyisaak.github.io/ginji-wanders</text>
</svg>
"""

def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    journal_text = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
    identity_text = (ROOT / "IDENTITY.md").read_text(encoding="utf-8")
    entries = parse_journal(journal_text)
    day_count = (ROOT / "DAY_COUNT").read_text(encoding="utf-8").strip() or "0"
    display_day = str(entries[0]["day"]) if entries else day_count
    paragraphs, rules = parse_identity(identity_text)
    entries_html, hidden_count = render_entries(entries)
    (DOCS / "index.html").write_text(build_html(display_day, entries_html, hidden_count, render_identity(paragraphs, rules)), encoding="utf-8")
    (DOCS / "style.css").write_text(build_css(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DOCS / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (DOCS / "og-image.svg").write_text(build_og_svg(display_day), encoding="utf-8")
    print("site built: docs/index.html, docs/style.css, docs/.nojekyll, docs/robots.txt, docs/sitemap.xml, docs/og-image.svg")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
