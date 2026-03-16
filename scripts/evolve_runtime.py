#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_HEADER = "timestamp\tday\titeration\tmetric\tdelta\tstatus\tdescription\n"
DEFAULT_SCOPE = [
    "src/ginji.py",
    "tests",
    "scripts/evolve_runtime.py",
    "scripts/metric_guard.py",
    "skills",
    "README.md",
    "docs/book/evolution.md",
    "wiki/evolution-pipeline.md",
    "wiki/testing-and-safety.md",
    "wiki/prompts-and-skills-system.md",
]


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def run_shell(command: str, *, timeout: int | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise RuntimeError((result.stdout or "") + (result.stderr or "") or f"command failed: {command}")
    return result


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def have_gh() -> bool:
    return shutil.which("gh") is not None and subprocess.run(
        ["gh", "auth", "status"], cwd=ROOT, capture_output=True, text=True
    ).returncode == 0


def ensure_results_log(results_path: Path) -> None:
    if not results_path.exists() or results_path.read_text(encoding="utf-8", errors="replace").splitlines()[:1] != [RESULTS_HEADER.strip()]:
        write_text(results_path, RESULTS_HEADER)


SESSION_FIELD_RE = re.compile(r"^([a-z_]+):\s*(.*)$")


def session_field(plan_path: Path, field_name: str) -> str:
    for line in read_text(plan_path).splitlines():
        match = SESSION_FIELD_RE.match(line.strip())
        if match and match.group(1).lower() == field_name.lower():
            return match.group(2).strip()
    return ""


def parse_scope_paths(scope_text: str) -> list[str]:
    return [part.strip() for part in scope_text.split(",") if part.strip()]


def write_default_session_plan(plan_path: Path, default_verify: str, build_check: str) -> None:
    write_text(
        plan_path,
        "\n".join(
            [
                "goal: increase tested capability coverage in the evolution harness runtime",
                "benchmark_gap: ginji still wastes healthy sessions on low-leverage maintenance because its mutable harness strategy is too implicit",
                "scope: scripts/evolve_runtime.py, skills/evolve/SKILL.md, skills/communicate/SKILL.md, tests/test_repo_integrity.py, tests/test_metric_guard.py, README.md, docs/book/evolution.md, wiki/evolution-pipeline.md, wiki/testing-and-safety.md, wiki/prompts-and-skills-system.md, EVOLUTION_RESULTS.tsv",
                "metric: total collected tests",
                "direction: higher",
                f"verify: {default_verify}",
                f"guard: {build_check}",
                "iteration_budget: 3",
                "stop_condition: stop after the first kept improvement or after 3 iterations",
                "---",
                "# rationale",
                "this fallback keeps the mutable harness measurable and focused on capability growth.",
                "",
                "# tasks",
                "1. tighten one mechanical check or prompt contract in the mutable harness.",
                "2. keep the change inside the declared scope.",
                "3. let the metric and guard decide whether the change stays.",
                "",
            ]
        ),
    )


def validate_session_plan(plan_path: Path) -> bool:
    required = ["goal", "benchmark_gap", "scope", "metric", "direction", "verify", "iteration_budget", "stop_condition"]
    for field_name in required:
        if not session_field(plan_path, field_name):
            return False
    direction = session_field(plan_path, "direction")
    if direction not in {"higher", "lower"}:
        return False
    budget = session_field(plan_path, "iteration_budget")
    return bool(re.fullmatch(r"\d+", budget))


def prepend_markdown_entry(target_path: Path, heading: str, entry_text: str) -> None:
    current = read_text(target_path)
    if current.startswith(f"{heading}\n"):
        rest = current.splitlines()[2:] if len(current.splitlines()) >= 2 else []
        write_text(target_path, f"{heading}\n\n{entry_text.strip()}\n\n" + "\n".join(rest).rstrip() + "\n")
    else:
        write_text(target_path, f"{heading}\n\n{entry_text.strip()}\n")


def prepend_journal_entry(day_num: int, entry_text: str) -> None:
    journal_path = ROOT / "JOURNAL.md"
    current = read_text(journal_path, "# journal\n")
    if re.search(rf"^## day {day_num} —", current, flags=re.M):
        return
    if current.startswith("# journal"):
        body = "\n".join(current.splitlines()[2:]).rstrip()
        merged = f"# journal\n\n{entry_text.strip()}\n"
        if body:
            merged += f"\n{body}\n"
        write_text(journal_path, merged)
    else:
        write_text(journal_path, f"# journal\n\n{entry_text.strip()}\n\n{current}")


def sanitize_journal_entry(entry_path: Path) -> None:
    if not entry_path.exists():
        return
    text = read_text(entry_path)
    text = re.sub(r"\s*explicit journal entry was written by the agent\.\s*", " ", text, flags=re.I)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    write_text(entry_path, text.strip() + "\n")


def restore_missing_journal_history(before_path: Path) -> None:
    journal_path = ROOT / "JOURNAL.md"
    if not before_path.exists() or not journal_path.exists():
        return
    pattern = re.compile(r"(^## day\s+\d+\s+—.*?)(?=^## day\s+\d+\s+—|\Z)", re.M | re.S)
    header = re.compile(r"^## day\s+(\d+)\s+—", re.M)

    def parse_entries(text: str) -> dict[int, str]:
        entries: dict[int, str] = {}
        for block in pattern.findall(text):
            match = header.search(block)
            if match:
                entries[int(match.group(1))] = block.strip()
        return entries

    before_entries = parse_entries(read_text(before_path))
    after_entries = parse_entries(read_text(journal_path))
    missing = [day for day in before_entries if day not in after_entries]
    if not missing:
        return
    merged_days = sorted(set(before_entries) | set(after_entries), reverse=True)
    merged_blocks = [after_entries.get(day, before_entries.get(day, "")).strip() for day in merged_days]
    merged_blocks = [block for block in merged_blocks if block]
    write_text(journal_path, "# journal\n\n" + "\n\n".join(merged_blocks).rstrip() + "\n")


def prepend_learnings_entry(day_num: int, entry_text: str) -> None:
    learnings_path = ROOT / "LEARNINGS.md"
    current = read_text(learnings_path, "# learnings\n")
    if re.search(rf"^\*\*learned:\*\* day {day_num}$", current, flags=re.M):
        return
    if current.startswith("# learnings"):
        body = "\n".join(current.splitlines()[2:]).rstrip()
        merged = f"# learnings\n\n{entry_text.strip()}\n"
        if body:
            merged += f"\n{body}\n"
        write_text(learnings_path, merged)
    else:
        write_text(learnings_path, f"# learnings\n\n{entry_text.strip()}\n\n{current}")


def append_fallback_journal(day_num: int, now_hhmm: str) -> None:
    prepend_journal_entry(
        day_num,
        "\n".join(
            [
                f"## day {day_num} — {now_hhmm} — measured session fallback",
                "",
                "i ran the mutable harness loop and kept the repo upright, but the normal journal writer still missed the branch.",
                "the kernel kept the day guard and the final build guard intact while the runtime handled the rest.",
                "that is useful, but i still want the sharper trail: exact file, exact command, exact edge case.",
                "next session i should keep the gain and tell the story more cleanly.",
            ]
        ),
    )


def append_fallback_learning(day_num: int) -> None:
    prepend_learnings_entry(
        day_num,
        "\n".join(
            [
                "## [mutable harnesses need fixed rails]",
                f"**learned:** day {day_num}",
                "**source:** evolution runtime execution",
                "moving strategy into a mutable runtime makes recursive improvement possible, but only if the day guard and final build gate stay outside that layer.",
                "the clean split is a small kernel for invariants and a richer runtime for tactics.",
            ]
        ),
    )


def snapshot_scope_state(snapshot_dir: Path, scope_paths: list[str]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    paths_file = snapshot_dir / "paths.txt"
    paths_file.write_text("\n".join(scope_paths) + "\n", encoding="utf-8")
    existing = [path for path in scope_paths if (ROOT / path).exists()]
    with tarfile.open(snapshot_dir / "scope.tar", "w") as tar:
        for path in existing:
            tar.add(ROOT / path, arcname=path)


def restore_scope_state(snapshot_dir: Path) -> None:
    paths = [line.strip() for line in read_text(snapshot_dir / "paths.txt").splitlines() if line.strip()]
    for path in paths:
        if path in {".", "/"}:
            continue
        target = ROOT / path
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        else:
            target.unlink(missing_ok=True)
    scope_tar = snapshot_dir / "scope.tar"
    if scope_tar.exists() and scope_tar.stat().st_size > 0:
        with tarfile.open(scope_tar, "r") as tar:
            tar.extractall(ROOT)


def latest_journal_day() -> int:
    journal = read_text(ROOT / "JOURNAL.md")
    match = re.search(r"^## day (\d+) —", journal, flags=re.M)
    return int(match.group(1)) if match else 0


def process_issue_responses(repo: str) -> None:
    issue_path = ROOT / "ISSUE_RESPONSE.md"
    if not issue_path.exists() or not have_gh():
        return
    blocks = read_text(issue_path).split("\n---\n")
    for block in blocks:
        issue_number = status = comment = ""
        for line in block.splitlines():
            if line.startswith("issue_number:"):
                issue_number = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                status = line.split(":", 1)[1].strip()
            elif line.startswith("comment:"):
                comment = line.split(":", 1)[1].strip()
            elif comment:
                comment += f" {line.strip()}"
        if not issue_number or not status or not comment:
            continue
        if subprocess.run(["gh", "issue", "view", issue_number, "--repo", repo], cwd=ROOT, capture_output=True, text=True).returncode != 0:
            continue
        subprocess.run(["gh", "issue", "comment", issue_number, "--repo", repo, "--body", comment], cwd=ROOT)
        if status in {"fixed", "wontfix"}:
            subprocess.run(["gh", "issue", "close", issue_number, "--repo", repo], cwd=ROOT)


def log_metric_result(results_path: Path, day_num: int, iteration: int, metric: str, delta: str, status: str, description: str) -> None:
    cleaned = re.sub(r"\s+", " ", description.strip())
    with results_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now().astimezone().isoformat()}\t{day_num}\t{iteration}\t{metric}\t{delta}\t{status}\t{cleaned}\n")


def measure_metric(command: str) -> str:
    result = subprocess.run(
        [sys.executable, "scripts/metric_guard.py", "measure", "--command", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "metric command failed")
    return result.stdout.strip()


def compare_metric(direction: str, baseline: str, candidate: str) -> tuple[str, str]:
    result = subprocess.run(
        [sys.executable, "scripts/metric_guard.py", "compare", "--direction", direction, "--baseline", baseline, "--candidate", candidate],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    status, delta = result.stdout.strip().split("\t", 1)
    return status, delta


def fetch_issue_digests(repo: str, day_num: int) -> None:
    if have_gh():
        issues_json = ROOT / ".tmp_ginji_issues.json"
        sponsors_json = ROOT / ".tmp_ginji_sponsors.json"
        subprocess.run(["gh", "api", f"repos/{repo}/issues?state=open&per_page=100"], cwd=ROOT, capture_output=True, text=True, check=False)
        issues_result = subprocess.run(["gh", "api", f"repos/{repo}/issues?state=open&per_page=100"], cwd=ROOT, capture_output=True, text=True, check=False)
        issues_json.write_text(issues_result.stdout if issues_result.returncode == 0 else "[]", encoding="utf-8")
        sponsors_json.write_text("[]", encoding="utf-8")
        run_shell(f"python scripts/format_issues.py {issues_json.name} {sponsors_json.name} {day_num}", check=True)
        formatted = run_shell(f"python scripts/format_issues.py {issues_json.name} {sponsors_json.name} {day_num}")
        write_text(ROOT / "ISSUES_TODAY.md", formatted.stdout)
        issues_json.unlink(missing_ok=True)
        sponsors_json.unlink(missing_ok=True)
        self_result = subprocess.run(["gh", "issue", "list", "--repo", repo, "--state", "open", "--label", "agent-self", "--limit", "100"], cwd=ROOT, capture_output=True, text=True)
        help_result = subprocess.run(["gh", "issue", "list", "--repo", repo, "--state", "open", "--label", "agent-help-wanted", "--limit", "100"], cwd=ROOT, capture_output=True, text=True)
        write_text(ROOT / "AGENT_SELF_ISSUES.md", self_result.stdout or "")
        write_text(ROOT / "AGENT_HELP_WANTED_ISSUES.md", help_result.stdout or "")
    else:
        write_text(ROOT / "ISSUES_TODAY.md", "no issues today.\n")
        write_text(ROOT / "AGENT_SELF_ISSUES.md", "gh unavailable\n")
        write_text(ROOT / "AGENT_HELP_WANTED_ISSUES.md", "gh unavailable\n")


def run_ginji_prompt(prompt_text: str, output_path: Path, *, timeout: int, model: str, ginji_bin: str) -> bool:
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as handle:
        handle.write(prompt_text)
        prompt_file = Path(handle.name)
    try:
        command = f"cat {prompt_file} | {ginji_bin} --model '{model}' --skills skills"
        result = run_shell(command, timeout=timeout, check=False)
        write_text(output_path, result.stdout)
        return result.returncode == 0
    except Exception:
        return False
    finally:
        prompt_file.unlink(missing_ok=True)


def main() -> int:
    repo = env("REPO", "brodyisaak/ginji-wanders")
    model = env("MODEL", "gpt-4o-mini")
    birth_date = env("BIRTH_DATE", "2026-03-07")
    ginji_bin = env("GINJI_BIN", "python src/ginji.py")
    build_check = env("BUILD_CHECK", "python -m py_compile src/ginji.py && python -m pytest tests/ -q")
    default_verify = env("DEFAULT_VERIFY", "python -m pytest tests/ --collect-only -q 2>/dev/null | tail -n 1 | awk '{print $1}'")
    timeout = int(env("TIMEOUT", "1200"))
    impl_timeout = int(env("IMPL_TIMEOUT", "900"))
    next_day = int(env("GINJI_NEXT_DAY", "1"))
    now_hhmm = env("GINJI_NOW_HHMM", "00:00")
    results_path = ROOT / env("RESULTS_LOG", "EVOLUTION_RESULTS.tsv")
    plan_path = ROOT / "SESSION_PLAN.md"
    journal_snapshot = Path(env("GINJI_JOURNAL_SNAPSHOT", str(ROOT / ".journal_snapshot.tmp")))

    ensure_results_log(results_path)
    fetch_issue_digests(repo, next_day)

    plan_prompt = f"""you are ginji, a self-evolving coding agent.
this is day {next_day} (born {birth_date}).
read these files before planning:
- IDENTITY.md
- PERSONALITY.md
- src/ginji.py
- JOURNAL.md
- LEARNINGS.md
- ISSUES_TODAY.md
- README.md
- wiki/index.md
- wiki/evolution-pipeline.md
- wiki/testing-and-safety.md
- wiki/prompts-and-skills-system.md
then run this command:
python -m pytest tests/ -q
write SESSION_PLAN.md in lowercase where appropriate.
choose one improvement only for this session.
prefer the highest-leverage capability-building improvement if the build is already healthy.
do not spend a healthy session on syntax cleanup, error handling, or input validation alone unless that issue is actively blocking another capability.
tie the chosen improvement to one benchmark ability a real coding agent needs: navigation, multi-file editing, test execution, git workflow, repo context, or recovery from failures.
write this exact machine-readable header first, one field per line, with single-line values:
goal: ...
benchmark_gap: ...
scope: path1, path2
metric: ...
direction: higher|lower
verify: ...
guard: ...
iteration_budget: 3
stop_condition: ...
after the header, write:
---
# rationale
[why this measured capability gain matters now]

# tasks
1. [task]
2. [task]
3. [task]
rules:
- the verify command must exit successfully and print one numeric metric when run in bash
- use the default build check as guard unless a stronger task-specific guard is needed
- scope should name repo files or directories, not globs
- prefer a task that compounds future throughput, not another isolated cleanup
"""
    run_ginji_prompt(plan_prompt, plan_path, timeout=timeout, model=model, ginji_bin=ginji_bin)
    if not validate_session_plan(plan_path):
        retry_prompt = "your last SESSION_PLAN.md was invalid. rewrite it now using the exact required header fields and make sure verify prints one number. keep the improvement measurable, capability-oriented, and scoped to repo paths."
        run_ginji_prompt(retry_prompt, ROOT / ".tmp_plan_retry.log", timeout=timeout, model=model, ginji_bin=ginji_bin)
    if not validate_session_plan(plan_path):
        write_default_session_plan(plan_path, default_verify, build_check)

    verify_command = session_field(plan_path, "verify") or default_verify
    guard_command = session_field(plan_path, "guard") or build_check
    direction = session_field(plan_path, "direction") or "higher"
    iteration_budget = int(session_field(plan_path, "iteration_budget") or "3")
    stop_condition = session_field(plan_path, "stop_condition")
    metric_name = session_field(plan_path, "metric") or "metric"
    scope_text = session_field(plan_path, "scope")
    scope_paths = parse_scope_paths(scope_text) or DEFAULT_SCOPE

    try:
        baseline_metric = measure_metric(verify_command)
    except Exception:
        write_default_session_plan(plan_path, default_verify, build_check)
        verify_command = session_field(plan_path, "verify")
        guard_command = session_field(plan_path, "guard")
        direction = session_field(plan_path, "direction")
        iteration_budget = int(session_field(plan_path, "iteration_budget"))
        stop_condition = session_field(plan_path, "stop_condition")
        metric_name = session_field(plan_path, "metric")
        scope_text = session_field(plan_path, "scope")
        scope_paths = parse_scope_paths(scope_text) or DEFAULT_SCOPE
        baseline_metric = measure_metric(verify_command)

    log_metric_result(results_path, next_day, 0, baseline_metric, "0", "baseline", f"baseline row for {metric_name}")
    best_metric = baseline_metric

    for iteration in range(1, iteration_budget + 1):
        snapshot_dir = Path(tempfile.mkdtemp())
        snapshot_scope_state(snapshot_dir, scope_paths)
        impl_prompt = f"""you are implementing iteration {iteration}/{iteration_budget} from SESSION_PLAN.md.
read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv before changing anything.
keep the change inside this declared scope only:
{scope_text}
current best metric for '{metric_name}': {best_metric}
direction: {direction}
verify command: {verify_command}
guard command: {guard_command}
requirements:
- make one atomic change only
- pick the next change most likely to improve the metric
- if this is the final iteration, exploit the strongest direction seen so far instead of trying a brand new angle
- do not do maintenance-only cleanup unless it directly improves the metric or prevents repeated failure in this scope
- do not rewrite SESSION_PLAN.md or EVOLUTION_RESULTS.tsv
- you may run local checks, but the runtime will decide keep or discard from the metric and guard
"""
        log_path = ROOT / f".tmp_ginji_impl_{iteration}.log"
        ok = run_ginji_prompt(impl_prompt, log_path, timeout=impl_timeout, model=model, ginji_bin=ginji_bin)
        if not ok:
            restore_scope_state(snapshot_dir)
            log_metric_result(results_path, next_day, iteration, best_metric, "0", "crash", f"iteration {iteration} agent execution failed")
            shutil.rmtree(snapshot_dir, ignore_errors=True)
            continue
        try:
            candidate_metric = measure_metric(verify_command)
        except Exception:
            restore_scope_state(snapshot_dir)
            log_metric_result(results_path, next_day, iteration, best_metric, "0", "crash", f"iteration {iteration} verify command failed")
            shutil.rmtree(snapshot_dir, ignore_errors=True)
            continue
        status, delta = compare_metric(direction, best_metric, candidate_metric)
        first_line = next((line.strip() for line in read_text(log_path).splitlines() if line.strip()), "")
        description = first_line or f"iteration {iteration} change inside {scope_text}"
        if status != "improved":
            restore_scope_state(snapshot_dir)
            log_metric_result(results_path, next_day, iteration, candidate_metric, delta, "discard", f"metric did not improve: {description}")
            shutil.rmtree(snapshot_dir, ignore_errors=True)
            continue
        guard_result = run_shell(guard_command, check=False)
        if guard_result.returncode != 0:
            restore_scope_state(snapshot_dir)
            log_metric_result(results_path, next_day, iteration, candidate_metric, delta, "discard", f"guard failed after improvement attempt: {description}")
            shutil.rmtree(snapshot_dir, ignore_errors=True)
            continue
        best_metric = candidate_metric
        log_metric_result(results_path, next_day, iteration, candidate_metric, delta, "keep", description)
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        if "first kept improvement" in stop_condition:
            break

    issue_prompt = "review SESSION_PLAN.md and your implementation logs. if you worked on any github issue, write ISSUE_RESPONSE.md exactly in the communicate skill format. if no issue work was done, do not create ISSUE_RESPONSE.md. keep lowercase and use ginji's small silver fox voice."
    run_ginji_prompt(issue_prompt, ROOT / ".tmp_issue_phase.log", timeout=impl_timeout, model=model, ginji_bin=ginji_bin)

    journal_prompt = f"""read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv.
write one journal entry to JOURNAL_ENTRY.md only.
do not rewrite JOURNAL.md directly.
format exactly:
## day {next_day} — {now_hhmm} — [short title]

requirements:
- 4 to 6 sentences in lowercase
- describe the kept capability gain, not discarded attempts
- mention at least one touched file path
- mention the exact verify or build command you ran
- mention the exact test or build command you ran
- mention the metric that moved or explain clearly if nothing improved
- mention one thing that was risky, blocked, or discarded
- keep technical clarity first, then add one light fox detail
- name the concrete bug, capability, or edge case you touched
- do not use template filler or say that you wrote a journal entry
- end with what is next
"""
    journal_entry = ROOT / "JOURNAL_ENTRY.md"
    run_ginji_prompt(journal_prompt, ROOT / ".tmp_journal.log", timeout=impl_timeout, model=model, ginji_bin=ginji_bin)
    sanitize_journal_entry(journal_entry)
    if journal_entry.exists() and re.search(rf"^## day {next_day} —", read_text(journal_entry), flags=re.M):
        prepend_journal_entry(next_day, read_text(journal_entry))
    if not re.search(rf"^## day {next_day} —", read_text(ROOT / "JOURNAL.md", ""), flags=re.M):
        append_fallback_journal(next_day, now_hhmm)
    restore_missing_journal_history(journal_snapshot)
    journal_entry.unlink(missing_ok=True)

    learning_prompt = f"""read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv.
write one learning entry to LEARNINGS_ENTRY.md only.
do not rewrite LEARNINGS.md directly.
format exactly:
## [short topic]
**learned:** day {next_day}
**source:** [session observation, test output, docs, or code review]
[2-4 sentences describing what moved the metric, what did not, and what that means for future sessions]
rules:
- focus on the measured loop, not generic motivation
- tie the learning to a concrete command, file, guard, or discarded attempt
- keep it lowercase
"""
    learnings_entry = ROOT / "LEARNINGS_ENTRY.md"
    run_ginji_prompt(learning_prompt, ROOT / ".tmp_learning.log", timeout=impl_timeout, model=model, ginji_bin=ginji_bin)
    if learnings_entry.exists() and re.search(rf"^\*\*learned:\*\* day {next_day}$", read_text(learnings_entry), flags=re.M):
        prepend_learnings_entry(next_day, read_text(learnings_entry))
    else:
        append_fallback_learning(next_day)
    learnings_entry.unlink(missing_ok=True)

    process_issue_responses(repo)
    run_shell("python scripts/build_site.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
