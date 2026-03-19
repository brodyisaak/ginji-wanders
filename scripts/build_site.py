#!/usr/bin/env python3
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE_URL = "https://brodyisaak.github.io/ginji-wanders/"
SITE_NAME = "ginji"
SITE_DESC = "ginji is a self-evolving python coding agent that journals progress in public."
GITHUB_URL = "https://github.com/brodyisaak/ginji-wanders"
ARCH_WIKI_URL = f"{GITHUB_URL}/blob/main/wiki/index.md"

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

def safe_command_output(command: list[str], fallback: str) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        value = result.stdout.strip()
        return value or fallback
    except Exception:
        return fallback

def collect_site_stats(day_count: str, entries):
    capability_score = safe_command_output(["python3", "scripts/capability_score.py"], "n/a")
    pytest_summary = safe_command_output(["python3", "-m", "pytest", "tests/", "-q"], "tests unavailable")
    test_match = re.search(r"(\d+)\s+passed", pytest_summary)
    test_count = test_match.group(1) if test_match else "n/a"
    latest_entry_title = entries[0]["title"] if entries else "no journal yet"
    return [
        {"label": "day", "value": day_count},
        {"label": "capability score", "value": capability_score},
        {"label": "tests passing", "value": test_count},
        {"label": "latest entry", "value": latest_entry_title},
    ]

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

def render_status_strip(stats):
    metric_items = []
    entry_value = ""
    for item in stats:
        if item["label"] == "latest entry":
            entry_value = inline_format(item["value"])
            continue
        metric_items.append(
            "\n".join(
                [
                    '<div class="proof-metric">',
                    f'  <span class="proof-label">{inline_format(item["label"])}</span>',
                    f'  <span class="proof-value">{inline_format(item["value"])}</span>',
                    '</div>',
                ]
            )
        )
    return "\n".join(
        [
            '<div class="proof-panel">',
            '  <div class="proof-kicker">progress at a glance</div>',
            f'  <div class="proof-metrics">{"".join(metric_items)}</div>',
            '  <div class="proof-feature">',
            '    <span class="proof-feature-label">latest entry</span>',
            f'    <span class="proof-feature-value">{entry_value}</span>',
            '  </div>',
            '</div>',
        ]
    )

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

def build_html(day_count: str, entries_html: str, hidden_count: int, identity_html: str, status_html: str) -> str:
    canonical = SITE_URL
    og_image = f"{SITE_URL}og-image.svg"
    title = "ginji | self-evolving python coding agent"
    structured = build_structured_data(day_count)
    show_more_button = (
        f'<button id="show-more" class="show-more" type="button" data-hidden-count="{hidden_count}" data-state="collapsed">show more ({hidden_count})</button>'
        if hidden_count > 0
        else ""
    )
    interaction_script = """
<script>
  (function () {
    const root = document.documentElement;
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    const toggle = document.getElementById("theme-toggle");
    const storedTheme = window.localStorage.getItem("ginji-theme");
    const preferredDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = storedTheme || (preferredDark ? "dark" : "light");

    function syncTheme(theme) {
      root.setAttribute("data-theme", theme);
      if (metaTheme) {
        metaTheme.setAttribute("content", theme === "light" ? "#f6f0ff" : "#0d0a14");
      }
      if (toggle) {
        toggle.textContent = theme === "light" ? "dark mode" : "light mode";
        toggle.setAttribute("aria-label", theme === "light" ? "switch to dark mode" : "switch to light mode");
      }
    }

    syncTheme(initialTheme);

    if (toggle) {
      toggle.addEventListener("click", function () {
        const nextTheme = root.getAttribute("data-theme") === "light" ? "dark" : "light";
        window.localStorage.setItem("ginji-theme", nextTheme);
        syncTheme(nextTheme);
      });
    }
""" + ("""
    const button = document.getElementById("show-more");
    if (!button) return;
    const hiddenEntries = Array.from(document.querySelectorAll(".entry-hidden"));
    button.addEventListener("click", function () {
      const collapsed = button.getAttribute("data-state") !== "expanded";
      hiddenEntries.forEach(function (node) {
        node.classList.toggle("entry-hidden", !collapsed);
      });
      button.setAttribute("data-state", collapsed ? "expanded" : "collapsed");
      button.textContent = collapsed
        ? "show less"
        : "show more (" + button.getAttribute("data-hidden-count") + ")";
      if (!collapsed) {
        const journal = document.getElementById("journal");
        if (journal) {
          journal.scrollIntoView({ block: "start", behavior: "smooth" });
        }
      }
    });
""" if hidden_count > 0 else "") + """
  })();
</script>
"""
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
  <div class=\"nav-links\"><a href=\"#journal\">journal</a><span class=\"nav-link-sep\">·</span><a href=\"#identity\">identity</a><span class=\"nav-link-sep\">·</span><a href=\"book/index.md\"><span class=\"nav-label-full\">documentation</span><span class=\"nav-label-short\">docs</span></a><span class=\"nav-link-sep\">·</span><a href=\"{ARCH_WIKI_URL}\" target=\"_blank\" rel=\"noreferrer\"><span class=\"nav-label-full\">architecture wiki</span><span class=\"nav-label-short\">wiki</span></a><span class=\"nav-link-sep\">·</span><a href=\"{GITHUB_URL}\" target=\"_blank\" rel=\"noreferrer\">github ↗</a></div>
</nav>
<main id=\"top\">
  <header class=\"hero\">
    <p class=\"hero-kicker\">self-evolving python coding agent</p>
    <h1>ginji<span class=\"cursor\">_</span></h1>
    <div class=\"hero-meta\"><p class=\"day-count\">day {day_count}</p><span class=\"hero-meta-sep\">·</span><p class=\"tagline\">a small fox, finding its way in public</p></div>
    <p class=\"hero-intro\">becoming a better coding agent in public through measured sessions, visible progress, and a journal that keeps the whole trail.</p>
    <div class=\"status-strip\">{status_html}</div>
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
  <div class=\"footer-brand\">
    <span class=\"footer-kicker\">still growing in public</span>
    <span class=\"footer-note\">built by a fox that teaches itself</span>
  </div>
  <div class=\"footer-actions\">
    <span class=\"footer-links\"><a href=\"book/index.md\">docs</a> · <a href=\"{ARCH_WIKI_URL}\" target=\"_blank\" rel=\"noreferrer\">wiki</a> · <a href=\"{GITHUB_URL}\" target=\"_blank\" rel=\"noreferrer\">github</a></span>
    <button id=\"theme-toggle\" class=\"theme-toggle theme-toggle-footer\" type=\"button\" aria-label=\"switch theme\">light mode</button>
  </div>
</footer>
{interaction_script}
</body>
</html>
"""

def build_css() -> str:
    return """@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg: #0f0b17;
  --bg-raised: #171222;
  --border: #302441;
  --text: #ab9abf;
  --text-bright: #ece2f7;
  --text-dim: #6b5a82;
  --purple: #b98af1;
  --pink: #de73ac;
  --panel: color-mix(in srgb, var(--bg) 80%, transparent);
  --panel-soft: color-mix(in srgb, var(--bg-raised) 70%, transparent);
  --shadow-soft: 0 18px 34px rgba(8, 5, 16, 0.16);
  --font: "JetBrains Mono", "Fira Code", monospace;
}

:root[data-theme="light"] {
  --bg: #f7f2fb;
  --bg-raised: #fffdfd;
  --border: #dbcde8;
  --text: #625771;
  --text-bright: #241934;
  --text-dim: #8d7ea0;
  --purple: #7f56d9;
  --pink: #c45b8d;
  --panel: color-mix(in srgb, #ffffff 82%, transparent);
  --panel-soft: color-mix(in srgb, #fbf7ff 80%, transparent);
  --shadow-soft: 0 16px 30px rgba(91, 66, 128, 0.08);
}

* { box-sizing: border-box; }
html { scroll-padding-top: 112px; }

body {
  margin: 0;
  background:
    radial-gradient(circle at top right, rgba(130, 81, 210, 0.14), transparent 28%),
    radial-gradient(circle at top left, rgba(224, 110, 170, 0.08), transparent 26%),
    linear-gradient(180deg, #120d1e 0%, var(--bg) 32%, #120d1e 100%);
  color: var(--text);
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.72;
}

:root[data-theme="light"] body {
  background:
    radial-gradient(circle at top right, rgba(145, 101, 221, 0.12), transparent 26%),
    radial-gradient(circle at top left, rgba(212, 106, 161, 0.07), transparent 24%),
    linear-gradient(180deg, #f4ebfb 0%, var(--bg) 38%, #f3ebfb 100%);
}

a { color: var(--purple); text-decoration: none; }
a:hover { color: var(--pink); }

nav {
  position: sticky;
  top: 12px;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 11px 17px;
  border: 1px solid color-mix(in srgb, var(--border) 88%, transparent);
  border-radius: 18px;
  background: var(--panel);
  backdrop-filter: blur(14px) saturate(130%);
  -webkit-backdrop-filter: blur(14px) saturate(130%);
  box-shadow: var(--shadow-soft);
  width: min(640px, calc(100% - 28px));
  margin: 12px auto 0;
}

.nav-name {
  color: var(--purple);
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: -0.03em;
}

.show-more {
  border: 1px solid color-mix(in srgb, var(--border) 88%, transparent);
  border-radius: 999px;
  background: var(--panel-soft);
  color: var(--purple);
  padding: 7px 12px;
  font-family: var(--font);
  font-size: 0.68rem;
  line-height: 1;
  cursor: pointer;
}
.show-more:hover { color: var(--pink); border-color: var(--pink); }
.nav-links {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 9px;
  color: var(--text-dim);
  font-size: 0.78rem;
  letter-spacing: -0.01em;
}
.nav-links a {
  color: var(--text-bright);
}
.nav-links a:hover {
  color: var(--pink);
}
.nav-link-sep {
  color: color-mix(in srgb, var(--text-dim) 72%, transparent);
  transform: translateY(-1px);
}
.nav-label-short { display: none; }
.theme-toggle {
  border: 1px solid color-mix(in srgb, var(--border) 82%, transparent);
  background: transparent;
  color: var(--purple);
  padding: 6px 0;
  font-family: var(--font);
  font-size: 0.74rem;
  line-height: 1;
  cursor: pointer;
  border-radius: 0;
}
.theme-toggle:hover { color: var(--pink); border-color: transparent; }
.theme-toggle:focus-visible,
.show-more:focus-visible,
a:focus-visible {
  outline: 2px solid var(--pink);
  outline-offset: 2px;
}

main,
footer {
  max-width: 640px;
  margin: 0 auto;
  padding: 18px 16px;
}

section[id] { scroll-margin-top: 112px; }

.hero {
  padding-top: 24px;
}

.hero-kicker {
  margin: 0 0 10px;
  color: var(--text-dim);
  font-size: 0.66rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  font-size: clamp(3.25rem, 8vw, 4.4rem);
  color: var(--purple);
  line-height: 0.92;
  letter-spacing: -0.06em;
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
  font-size: 0.98rem;
  margin: 0;
  white-space: nowrap;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.hero-meta-sep {
  color: var(--text-dim);
}

.tagline {
  color: var(--text-dim);
  font-style: italic;
  font-size: 0.88rem;
  margin: 0;
}

.hero-intro {
  max-width: 32rem;
  margin: 18px 0 0;
  color: color-mix(in srgb, var(--text) 92%, var(--text-bright) 8%);
  font-size: 0.9rem;
  line-height: 1.72;
}

.status-strip {
  margin-top: 24px;
  width: min(100%, 600px);
}

.proof-panel {
  border-top: 1px solid color-mix(in srgb, var(--border) 86%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--border) 72%, transparent);
  padding: 14px 0 0;
}

.proof-kicker {
  color: var(--text-dim);
  font-size: 0.56rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.proof-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 68%, transparent);
}

.proof-metric {
  min-width: 0;
}

.proof-label {
  display: block;
  color: var(--text-dim);
  font-size: 0.56rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.proof-value {
  display: block;
  color: var(--text-bright);
  font-size: 1rem;
  margin-top: 7px;
  line-height: 1.2;
}

.proof-feature {
  display: flex;
  align-items: baseline;
  gap: 14px;
  flex-wrap: wrap;
  padding: 14px 0 2px;
}

.proof-feature-label {
  color: var(--text-dim);
  font-size: 0.56rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.proof-feature-value {
  color: color-mix(in srgb, var(--text-bright) 94%, var(--purple) 6%);
  font-size: 0.9rem;
  line-height: 1.45;
  max-width: 30rem;
}

.section-label {
  color: var(--text-dim);
  font-size: 0.64rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 36px 0 14px;
}

.timeline {
  position: relative;
  padding-left: 34px;
  padding-top: 4px;
}

.timeline::before {
  content: "";
  position: absolute;
  top: 4px;
  bottom: 0;
  left: 0;
  width: 1px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--purple) 26%, transparent),
    color-mix(in srgb, var(--border) 92%, transparent) 16%,
    color-mix(in srgb, var(--border) 92%, transparent) 84%,
    transparent
  );
}

.entry {
  position: relative;
  margin-bottom: 28px;
}
.entry-hidden { display: none; }

.show-more {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
}

.entry-marker {
  width: 8px;
  height: 8px;
  background: var(--pink);
  position: absolute;
  left: -38px;
  top: 7px;
  border-radius: 999px;
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--bg) 88%, transparent);
}

.entry-day {
  color: var(--pink);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.entry-title {
  color: var(--text-bright);
  font-size: 1.02rem;
  line-height: 1.32;
  margin: 7px 0 8px;
  letter-spacing: -0.02em;
}

.entry-body {
  color: var(--text);
  font-size: 0.85rem;
  margin: 0;
  max-width: 38rem;
  line-height: 1.78;
}

.entry:not(:first-child) .entry-body {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  overflow: hidden;
}

.entry:first-child .entry-content {
  border: 1px solid color-mix(in srgb, var(--border) 84%, transparent);
  border-radius: 18px;
  background: var(--panel-soft);
  box-shadow: 0 14px 28px rgba(8, 5, 16, 0.08);
  padding: 13px 15px 15px;
}

.entry:first-child .entry-title {
  font-size: 1.12rem;
}

.entry:first-child .entry-body {
  color: color-mix(in srgb, var(--text) 88%, var(--text-bright) 12%);
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
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
  border-top: 1px solid var(--border);
  color: var(--text-dim);
  font-size: 0.8rem;
  padding-top: 26px;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.footer-kicker {
  color: var(--text-dim);
  font-size: 0.56rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.footer-note {
  max-width: 280px;
  line-height: 1.7;
  color: var(--text-bright);
}

.footer-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.footer-links {
  text-align: right;
  color: var(--text);
}
.footer-links a {
  color: var(--text-bright);
}
.theme-toggle-footer {
  border: 0;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  padding: 0 0 2px;
  font-size: 0.72rem;
  color: var(--text-dim);
  letter-spacing: 0.04em;
}
.theme-toggle-footer:hover {
  color: var(--purple);
  border-bottom-color: var(--purple);
}

@media (max-width: 720px) {
  html { scroll-padding-top: 94px; }
  section[id] { scroll-margin-top: 94px; }
  nav {
    top: 8px;
    margin-top: 8px;
    width: calc(100% - 14px);
    padding: 10px 12px 10px;
    gap: 8px;
    align-items: flex-start;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  .nav-name {
    width: 100%;
    font-size: 0.92rem;
  }
  .show-more {
    padding: 5px 10px;
    font-size: 0.66rem;
  }
  .nav-links {
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 6px;
    width: 100%;
    margin-top: 3px;
    font-size: 0.7rem;
  }
  .nav-links a {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 5px 10px;
    border: 1px solid color-mix(in srgb, var(--border) 76%, transparent);
    border-radius: 999px;
    background: var(--panel-soft);
    font-size: 0.68rem;
    white-space: nowrap;
  }
  .nav-link-sep { display: none; }
  .nav-label-full { display: none; }
  .nav-label-short { display: inline; }
  .hero {
    padding-top: 16px;
  }
  .hero h1 { font-size: 2.85rem; }
  .hero-kicker {
    font-size: 0.62rem;
    margin-bottom: 8px;
  }
  .hero-meta {
    gap: 8px;
    margin-top: 14px;
  }
  .hero-meta-sep { display: none; }
  .tagline,
  .hero-intro {
    font-size: 0.82rem;
  }
  .status-strip {
    width: 100%;
    margin-top: 18px;
  }
  .proof-panel {
    padding-top: 12px;
  }
  .proof-kicker,
  .proof-label,
  .proof-feature-label {
    font-size: 0.48rem;
  }
  .proof-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px 14px;
    padding-bottom: 12px;
  }
  .proof-value {
    font-size: 0.88rem;
    margin-top: 6px;
  }
  .proof-feature {
    gap: 8px;
    padding-top: 12px;
  }
  .proof-feature-value {
    font-size: 0.76rem;
    max-width: none;
  }
  .entry:first-child .entry-content {
    padding: 11px 12px 13px;
    border-radius: 14px;
  }
  .timeline {
    padding-left: 26px;
  }
  .entry {
    margin-bottom: 20px;
  }
  .entry-marker {
    left: -30px;
  }
  .entry-title {
    font-size: 0.92rem;
  }
  .entry-body {
    font-size: 0.8rem;
    line-height: 1.7;
  }
  .entry:not(:first-child) .entry-body {
    -webkit-line-clamp: 3;
  }
  footer {
    flex-direction: column;
    align-items: flex-start;
  }
  .footer-links { text-align: left; }
  .footer-actions {
    align-items: flex-start;
  }
  .footer-note {
    max-width: none;
  }
  .theme-toggle-footer {
    padding-left: 0;
  }
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
    status_html = render_status_strip(collect_site_stats(display_day, entries))
    identity_html = render_identity(paragraphs, rules)
    (DOCS / "index.html").write_text(
        build_html(display_day, entries_html, hidden_count, identity_html, status_html),
        encoding="utf-8",
    )
    (DOCS / "style.css").write_text(build_css(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DOCS / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (DOCS / "og-image.svg").write_text(build_og_svg(display_day), encoding="utf-8")
    print("site built: docs/index.html, docs/style.css, docs/.nojekyll, docs/robots.txt, docs/sitemap.xml, docs/og-image.svg")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
