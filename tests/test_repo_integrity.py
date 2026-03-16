from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BANNED_PATTERNS = [r"\byoyo\b", r"\byologdev\b", r"\byolo\b"]
TEXT_EXTENSIONS = {".md", ".py", ".sh", ".yml", ".yaml", ".txt", ".html", ".css", ".svg"}


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def text_files():
    files = []
    for rel in tracked_files():
        if rel.suffix.lower() in TEXT_EXTENSIONS:
            files.append(rel)
    return files


def test_no_external_branding_outside_builder_input():
    offenders = []
    regexes = [re.compile(pat, flags=re.IGNORECASE) for pat in BANNED_PATTERNS]

    for rel in text_files():
        # builder-input is intentionally a local scratch area.
        if str(rel).startswith("builder-input/"):
            continue
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for rx in regexes:
            if rx.search(text):
                offenders.append(f"{rel}: pattern '{rx.pattern}'")

    assert not offenders, "found banned external branding:\n" + "\n".join(offenders)


def test_wiki_relative_links_resolve():
    missing = []
    for page in (ROOT / "wiki").glob("*.md"):
        text = page.read_text(encoding="utf-8", errors="replace")
        for target in re.findall(r"\]\((\./[^)]+\.md)\)", text):
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{page.relative_to(ROOT)} -> {target}")

    assert not missing, "found broken wiki links:\n" + "\n".join(missing)


def test_readme_links_to_wiki_hub():
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    assert "wiki/index.md" in readme


def test_evolution_rules_prioritize_capability_growth():
    evolve_skill = (ROOT / "skills" / "evolve" / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")

    assert "capability priority ladder" in evolve_skill
    assert "measured session contract" in evolve_skill
    assert "prefer improvements that move ginji toward real coding-agent utility" in evolve_skill
    assert "do not spend a healthy session on syntax cleanup, error handling, or input validation alone" in evolve_script
    assert "benchmark ability a real coding agent needs" in evolve_script


def test_journal_prompt_requires_specifics():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")

    assert "mention the exact test or build command you ran" in evolve_script
    assert "name the concrete bug, capability, or edge case you touched" in evolve_script


def test_metric_loop_language_is_present():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")

    assert "goal:" in evolve_script
    assert "benchmark_gap:" in evolve_script
    assert "verify:" in evolve_script
    assert "guard:" in evolve_script
    assert "iteration_budget:" in evolve_script
    assert "EVOLUTION_RESULTS.tsv" in evolve_script
    assert "baseline metric" in evolve_script or "baseline row" in evolve_script
    assert "bounded internal iteration loop" in readme


def test_repo_does_not_depend_on_local_skill_scratch_folder():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")

    assert "skill/autoresearch" not in evolve_script
    assert "skill/autoresearch" not in readme
