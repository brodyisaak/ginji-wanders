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
    evolve_runtime = (ROOT / "scripts" / "evolve_runtime.py").read_text(encoding="utf-8", errors="replace")

    assert "capability priority ladder" in evolve_skill
    assert "recursive harness rule" in evolve_skill
    assert "measured session contract" in evolve_skill
    assert "prefer improvements that move ginji toward real coding-agent utility" in evolve_skill
    assert "do not spend a healthy session on syntax cleanup, error handling, or input validation alone" in evolve_runtime
    assert "benchmark ability a real coding agent needs" in evolve_runtime
    assert "if the same benchmark gap fails to produce a kept gain for 2 sessions" in evolve_skill
    assert "if the same benchmark ability has stalled for 2 sessions without a kept metric gain" in evolve_runtime
    assert "prefer a safer open non-git lane" in evolve_skill
    assert "use the live gap snapshot" in evolve_skill
    assert "only test it inside temporary repos or other isolated sandboxes" in evolve_runtime
    assert "never mutate the project repo" in evolve_skill


def test_journal_prompt_requires_specifics():
    evolve_runtime = (ROOT / "scripts" / "evolve_runtime.py").read_text(encoding="utf-8", errors="replace")

    assert "mention the exact test or build command you ran" in evolve_runtime
    assert "name the concrete bug, capability, or edge case you touched" in evolve_runtime
    assert ".tmp_session_summary.md" in evolve_runtime
    assert "ground the entry in .tmp_session_summary.md" in evolve_runtime


def test_metric_loop_language_is_present():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")
    evolve_runtime = (ROOT / "scripts" / "evolve_runtime.py").read_text(encoding="utf-8", errors="replace")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")

    assert "scripts/evolve_runtime.py" in evolve_script
    assert "final build guard before publish" in evolve_script
    assert "goal:" in evolve_runtime
    assert "benchmark_gap:" in evolve_runtime
    assert "verify:" in evolve_runtime
    assert "guard:" in evolve_runtime
    assert "iteration_budget:" in evolve_runtime
    assert "EVOLUTION_RESULTS.tsv" in evolve_runtime
    assert "baseline row" in evolve_runtime
    assert "normalize_results_rows" in evolve_runtime
    assert "write_session_summary" in evolve_runtime
    assert "bounded internal iteration loop" in readme


def test_repo_does_not_depend_on_local_skill_scratch_folder():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")
    evolve_runtime = (ROOT / "scripts" / "evolve_runtime.py").read_text(encoding="utf-8", errors="replace")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")

    assert "skill/autoresearch" not in evolve_script
    assert "skill/autoresearch" not in evolve_runtime
    assert "skill/autoresearch" not in readme


def test_kernel_runtime_split_is_explicit():
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")
    evolve_runtime = (ROOT / "scripts" / "evolve_runtime.py").read_text(encoding="utf-8", errors="replace")
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")

    assert "protected kernel" in readme
    assert "mutable harness layer" in readme
    assert "python scripts/evolve_runtime.py" in evolve_script
    assert "kernel: final build guard before publish" in evolve_script
    assert "restore_missing_journal_history" in evolve_script
    assert "run_ginji_prompt" in evolve_runtime


def test_evolution_retry_policy_is_fast_and_selective():
    workflow = (ROOT / ".github" / "workflows" / "evolve.yml").read_text(encoding="utf-8", errors="replace")
    evolve_script = (ROOT / "scripts" / "evolve.sh").read_text(encoding="utf-8", errors="replace")

    assert "retry after 5min for transient runtime failures" in workflow
    assert "steps.attempt1.outputs.retryable == 'true'" in workflow
    assert "sleep 300" in workflow
    assert "sleep 900" not in workflow
    assert "sleep 2700" not in workflow
    assert ".evolve_failure_kind" in workflow
    assert 'DEFAULT_VERIFY="python scripts/capability_score.py"' in evolve_script
    assert 'mark_failure "deterministic-build"' in evolve_script
    assert 'mark_failure "transient-runtime"' in evolve_script
