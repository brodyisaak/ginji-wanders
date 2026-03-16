#!/bin/bash
set -euo pipefail

REPO="brodyisaak/ginji-wanders"
PROJECT_NAME="ginji-wanders"
MODEL="gpt-4o-mini"
BIRTH_DATE="2026-03-07"
GINJI_BIN="python src/ginji.py"
BUILD_CHECK='python -m py_compile src/ginji.py && python -m pytest tests/ -q'
DEFAULT_VERIFY="python -m pytest tests/ --collect-only -q 2>/dev/null | tail -n 1 | awk '{print \$1}'"
TIMEOUT="${TIMEOUT:-1200}"
IMPL_TIMEOUT="${IMPL_TIMEOUT:-900}"
RESULTS_LOG="EVOLUTION_RESULTS.tsv"

BOT_NAME="ginji-wanders[bot]"
BOT_EMAIL="ginji-wanders[bot]@users.noreply.github.com"

run_with_timeout() {
  local seconds="$1"
  shift
  local command="$*"

  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$seconds" bash -lc "$command"
    return $?
  fi

  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" bash -lc "$command"
    return $?
  fi

  bash -lc "$command" &
  local pid=$!
  (
    sleep "$seconds"
    if kill -0 "$pid" >/dev/null 2>&1; then
      echo "command timed out after ${seconds}s"
      kill "$pid" >/dev/null 2>&1 || true
    fi
  ) &
  local watcher=$!
  set +e
  wait "$pid"
  local status=$?
  set -e
  kill "$watcher" >/dev/null 2>&1 || true
  return "$status"
}

have_gh() {
  command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1
}

session_field() {
  local file_path="$1"
  local field_name="$2"
  python - "$file_path" "$field_name" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
field = sys.argv[2].strip().lower()
if not path.exists():
    raise SystemExit(1)
for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
    if ":" not in line:
        continue
    key, value = line.split(":", 1)
    if key.strip().lower() == field:
        print(value.strip())
        raise SystemExit(0)
raise SystemExit(1)
PY
}

parse_scope_paths() {
  local scope_text="$1"
  python - "$scope_text" <<'PY'
import sys
items = []
for part in sys.argv[1].split(','):
    value = part.strip()
    if value:
        items.append(value)
for item in items:
    print(item)
PY
}

ensure_results_log() {
  if [[ ! -f "$RESULTS_LOG" ]] || ! head -n 1 "$RESULTS_LOG" | grep -q $'^timestamp\tday\titeration\tmetric\tdelta\tstatus\tdescription$'; then
    echo $'timestamp\tday\titeration\tmetric\tdelta\tstatus\tdescription' > "$RESULTS_LOG"
  fi
}

log_metric_result() {
  local day_num="$1"
  local iteration="$2"
  local metric_value="$3"
  local delta_value="$4"
  local status="$5"
  local description="$6"
  local cleaned
  cleaned="$(printf '%s' "$description" | tr '\t\n' '  ' | sed 's/  */ /g' | sed 's/^ //; s/ $//')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(TZ=America/Los_Angeles date +%Y-%m-%dT%H:%M:%S%z)" "$day_num" "$iteration" "$metric_value" "$delta_value" "$status" "$cleaned" >> "$RESULTS_LOG"
}

measure_metric_value() {
  local command_text="$1"
  python scripts/metric_guard.py measure --command "$command_text"
}

compare_metric_values() {
  local direction="$1"
  local baseline="$2"
  local candidate="$3"
  python scripts/metric_guard.py compare --direction "$direction" --baseline "$baseline" --candidate "$candidate"
}

write_default_session_plan() {
  cat > SESSION_PLAN.md <<EOF_PLAN
goal: increase tested capability coverage in the evolution harness
benchmark_gap: ginji still wastes healthy sessions on low-leverage maintenance because planning does not require a measurable capability target
scope: scripts/evolve.sh, skills/evolve/SKILL.md, skills/communicate/SKILL.md, tests/test_repo_integrity.py, tests/test_metric_guard.py, README.md, docs/book/evolution.md, wiki/evolution-pipeline.md, wiki/testing-and-safety.md, wiki/prompts-and-skills-system.md, EVOLUTION_RESULTS.tsv
metric: total collected tests
direction: higher
verify: ${DEFAULT_VERIFY}
guard: ${BUILD_CHECK}
iteration_budget: 3
stop_condition: stop after the first kept improvement or after 3 iterations
---
# rationale
this fallback keeps the session measurable and pushes ginji toward stronger harnessing instead of another hygiene-only loop.

# tasks
1. add or tighten one mechanical check that raises the measured capability floor.
2. keep the change scoped to the declared files.
3. let the harness verify improvement mechanically before keeping it.
EOF_PLAN
}

validate_session_plan() {
  local plan_ok=1
  local required_fields=(goal benchmark_gap scope metric direction verify iteration_budget stop_condition)
  for field_name in "${required_fields[@]}"; do
    if ! session_field SESSION_PLAN.md "$field_name" >/dev/null 2>&1; then
      echo "missing session field: ${field_name}"
      plan_ok=0
    fi
  done

  local direction_value=""
  direction_value="$(session_field SESSION_PLAN.md direction 2>/dev/null || true)"
  if [[ -n "$direction_value" && "$direction_value" != "higher" && "$direction_value" != "lower" ]]; then
    echo "invalid direction: ${direction_value}"
    plan_ok=0
  fi

  local iteration_budget=""
  iteration_budget="$(session_field SESSION_PLAN.md iteration_budget 2>/dev/null || true)"
  if [[ -n "$iteration_budget" && ! "$iteration_budget" =~ ^[0-9]+$ ]]; then
    echo "invalid iteration budget: ${iteration_budget}"
    plan_ok=0
  fi

  if [[ "$plan_ok" -eq 1 ]]; then
    return 0
  fi
  return 1
}

append_fallback_journal() {
  local day_num="$1"
  local now_hhmm="$2"
  local entry_tmp
  entry_tmp="$(mktemp)"
  {
    echo "## day ${day_num} — ${now_hhmm} — measured session fallback"
    echo
    echo "i ran the new metric loop all the way through and kept the repo standing, but the normal journal writer still missed the branch." 
    echo "the harness captured a baseline, checked the guard, and rebuilt the site without losing the trail."
    echo "that is useful, but i still want a sharper entry with the real file, command, and edge case from the day."
    echo "next session i should keep the measured gain and tell the story with cleaner paws."
  } > "$entry_tmp"
  prepend_journal_entry "$day_num" "$entry_tmp"
  rm -f "$entry_tmp"
}

latest_journal_day() {
  if [[ ! -f JOURNAL.md ]]; then
    echo "0"
    return
  fi
  local latest
  latest="$(grep -E '^## day [0-9]+ —' JOURNAL.md | head -n 1 | sed -E 's/^## day ([0-9]+) —.*/\1/' || true)"
  if [[ -z "$latest" ]]; then
    echo "0"
  else
    echo "$latest"
  fi
}

prepend_journal_entry() {
  local day_num="$1"
  local entry_file="$2"
  local tmp
  tmp="$(mktemp)"
  if [[ -f JOURNAL.md ]] && grep -q "^## day ${day_num} —" JOURNAL.md; then
    return
  fi

  if [[ -f JOURNAL.md ]] && head -n 1 JOURNAL.md | grep -q '^# journal'; then
    {
      echo "# journal"
      echo
      cat "$entry_file"
      echo
      tail -n +3 JOURNAL.md
    } > "$tmp"
  else
    {
      echo "# journal"
      echo
      cat "$entry_file"
      echo
      [[ -f JOURNAL.md ]] && cat JOURNAL.md
    } > "$tmp"
  fi
  mv "$tmp" JOURNAL.md
}

sanitize_journal_entry() {
  local entry_file="$1"
  if [[ ! -f "$entry_file" ]]; then
    return
  fi
  python - "$entry_file" <<'PY'
import re
import sys
from pathlib import Path

entry_path = Path(sys.argv[1])
text = entry_path.read_text(encoding="utf-8")
text = re.sub(r"\s*explicit journal entry was written by the agent\.\s*", " ", text, flags=re.IGNORECASE)
text = re.sub(r"[ \t]+\n", "\n", text)
text = re.sub(r"\n{3,}", "\n\n", text)
entry_path.write_text(text.strip() + "\n", encoding="utf-8")
PY
}

restore_missing_journal_history() {
  local before_file="$1"
  if [[ ! -f "$before_file" || ! -f JOURNAL.md ]]; then
    return
  fi
  python - "$before_file" JOURNAL.md <<'PY'
import re
import sys
from pathlib import Path

before_path = Path(sys.argv[1])
after_path = Path(sys.argv[2])

before = before_path.read_text(encoding="utf-8")
after = after_path.read_text(encoding="utf-8")

pattern = re.compile(r"(^## day\s+\d+\s+—.*?)(?=^## day\s+\d+\s+—|\Z)", re.M | re.S)
day_header = re.compile(r"^## day\s+(\d+)\s+—", re.M)

def parse_entries(text: str):
    entries = {}
    for block in pattern.findall(text):
        match = day_header.search(block)
        if not match:
            continue
        day_num = int(match.group(1))
        entries[day_num] = block.strip()
    return entries

before_entries = parse_entries(before)
after_entries = parse_entries(after)

missing = [d for d in before_entries if d not in after_entries]
if not missing:
    print("journal history check: no missing days")
    raise SystemExit(0)

merged_days = sorted(set(before_entries) | set(after_entries), reverse=True)
merged_blocks = [after_entries.get(day, before_entries.get(day, "")).strip() for day in merged_days]
merged_blocks = [b for b in merged_blocks if b]

output = "# journal\n\n" + "\n\n".join(merged_blocks).rstrip() + "\n"
after_path.write_text(output, encoding="utf-8")
print(f"journal history restored: added {len(missing)} missing day entries")
PY
}

prepend_learnings_entry() {
  local day_num="$1"
  local entry_file="$2"
  local tmp
  tmp="$(mktemp)"
  if [[ -f LEARNINGS.md ]] && grep -q "^\\*\\*learned:\\*\\* day ${day_num}$" LEARNINGS.md; then
    return
  fi

  if [[ -f LEARNINGS.md ]] && head -n 1 LEARNINGS.md | grep -q '^# learnings'; then
    {
      echo "# learnings"
      echo
      cat "$entry_file"
      echo
      tail -n +3 LEARNINGS.md
    } > "$tmp"
  else
    {
      echo "# learnings"
      echo
      cat "$entry_file"
      echo
      echo "things i've looked up and want to remember. saves me from searching for the same thing twice."
      echo
      echo "<!-- format:"
      echo "## [topic]"
      echo "**learned:** day n"
      echo "**source:** [url or description]"
      echo "[what i learned]"
      echo "-->"
    } > "$tmp"
  fi
  mv "$tmp" LEARNINGS.md
}

append_fallback_learning() {
  local day_num="$1"
  local tmp
  tmp="$(mktemp)"
  {
    echo "## [measured capability loops beat vague cleanup]"
    echo "**learned:** day ${day_num}"
    echo "**source:** evolution session execution"
    echo "forcing a baseline, metric, and guard keeps the session honest and makes low-leverage cleanup easier to reject."
    echo "when the loop records keeps and discards explicitly, the next session has a better trail to follow."
  } > "$tmp"
  prepend_learnings_entry "$day_num" "$tmp"
  rm -f "$tmp"
}

snapshot_scope_state() {
  local snapshot_dir="$1"
  shift
  mkdir -p "$snapshot_dir"
  : > "$snapshot_dir/paths.txt"
  local -a existing_paths=()
  for path in "$@"; do
    [[ -z "$path" ]] && continue
    printf '%s\n' "$path" >> "$snapshot_dir/paths.txt"
    if [[ -e "$path" ]]; then
      existing_paths+=("$path")
    fi
  done
  if [[ "${#existing_paths[@]}" -gt 0 ]]; then
    tar -cf "$snapshot_dir/scope.tar" "${existing_paths[@]}"
  else
    : > "$snapshot_dir/scope.tar"
  fi
}

restore_scope_state() {
  local snapshot_dir="$1"
  if [[ ! -d "$snapshot_dir" ]]; then
    return
  fi
  while IFS= read -r path || [[ -n "$path" ]]; do
    [[ -z "$path" ]] && continue
    if [[ "$path" == "." || "$path" == "/" ]]; then
      continue
    fi
    rm -rf "$path"
  done < "$snapshot_dir/paths.txt"
  if [[ -s "$snapshot_dir/scope.tar" ]]; then
    tar -xf "$snapshot_dir/scope.tar"
  fi
}

process_issue_responses() {
  if [[ ! -f ISSUE_RESPONSE.md ]]; then
    echo "no issue response file found."
    return
  fi
  if ! have_gh; then
    echo "gh unavailable, skipping issue response processing."
    return
  fi

  local issue_number=""
  local status=""
  local comment=""

  flush_response() {
    if [[ -z "$issue_number" || -z "$status" || -z "$comment" ]]; then
      return
    fi
    if ! gh issue view "$issue_number" --repo "$REPO" >/dev/null 2>&1; then
      echo "skipping unknown issue #${issue_number}"
      return
    fi
    echo "posting response to issue #${issue_number}"
    gh issue comment "$issue_number" --repo "$REPO" --body "$comment" || true
    if [[ "$status" == "fixed" || "$status" == "wontfix" ]]; then
      gh issue close "$issue_number" --repo "$REPO" || true
    fi
  }

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "---" ]]; then
      flush_response
      issue_number=""
      status=""
      comment=""
      continue
    fi
    case "$line" in
      issue_number:*) issue_number="${line#issue_number: }" ;;
      status:*) status="${line#status: }" ;;
      comment:*) comment="${line#comment: }" ;;
      *)
        if [[ -n "$comment" ]]; then
          comment+=" ${line}"
        fi
        ;;
    esac
  done < ISSUE_RESPONSE.md

  flush_response
}

echo "starting ${PROJECT_NAME} evolution run"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "missing OPENAI_API_KEY"
  exit 1
fi

if [[ -n "${GH_PAT:-}" && -z "${GH_TOKEN:-}" ]]; then
  export GH_TOKEN="$GH_PAT"
fi

git config user.name "$BOT_NAME"
git config user.email "$BOT_EMAIL"

current_day="0"
if [[ -f DAY_COUNT ]]; then
  current_day="$(tr -d '[:space:]' < DAY_COUNT)"
fi
if ! [[ "$current_day" =~ ^[0-9]+$ ]]; then
  current_day="0"
fi
next_day="$((current_day + 1))"
now_hhmm="$(TZ=America/Los_Angeles date +%H:%M)"
today_pst="$(TZ=America/Los_Angeles date +%Y-%m-%d)"
last_post_pst=""
if [[ -f LAST_POST_DATE_PST ]]; then
  last_post_pst="$(tr -d '[:space:]' < LAST_POST_DATE_PST)"
fi
if [[ "$last_post_pst" == "$today_pst" ]]; then
  echo "already posted today in pacific time (${today_pst}); skipping."
  exit 0
fi

journal_history_snapshot="$(mktemp)"
if [[ -f JOURNAL.md ]]; then
  cp JOURNAL.md "$journal_history_snapshot"
else
  echo "# journal" > "$journal_history_snapshot"
fi

ensure_results_log

echo "step 0: verify build"
bash -lc "$BUILD_CHECK"

echo "step 1: check previous ci status via gh"
if have_gh; then
  gh run list --repo "$REPO" --workflow ci --limit 1 --json status,conclusion,displayTitle,createdAt > /tmp/ginji_prev_ci.json || true
  cat /tmp/ginji_prev_ci.json || true
else
  echo "gh unavailable, skipping ci status check"
fi

echo "step 2: fetch github issues and format digest"
if have_gh; then
  gh api "repos/$REPO/issues?state=open&per_page=100" > /tmp/ginji_issues.json || echo "[]" > /tmp/ginji_issues.json
  echo "[]" > /tmp/ginji_sponsors.json
  python scripts/format_issues.py /tmp/ginji_issues.json /tmp/ginji_sponsors.json "$next_day" > ISSUES_TODAY.md
else
  echo "no issues today." > ISSUES_TODAY.md
fi

echo "step 3: fetch agent-self and agent-help-wanted issues"
if have_gh; then
  gh issue list --repo "$REPO" --state open --label "agent-self" --limit 100 > AGENT_SELF_ISSUES.md || true
  gh issue list --repo "$REPO" --state open --label "agent-help-wanted" --limit 100 > AGENT_HELP_WANTED_ISSUES.md || true
else
  echo "gh unavailable" > AGENT_SELF_ISSUES.md
  echo "gh unavailable" > AGENT_HELP_WANTED_ISSUES.md
fi

echo "step 4: planning session (phase a)"
cat > /tmp/ginji_plan_prompt.txt <<EOF_PLAN_PROMPT
you are ginji, a self-evolving coding agent.
this is day ${next_day} (born ${BIRTH_DATE}).
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
- do not reference external command names or external branding
- prefer a task that compounds future throughput, not another isolated cleanup
EOF_PLAN_PROMPT

run_with_timeout "$TIMEOUT" "cat /tmp/ginji_plan_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > SESSION_PLAN.md || true

if [[ ! -s SESSION_PLAN.md ]] || ! validate_session_plan; then
  echo "planning retry: invalid or empty session plan"
  cat > /tmp/ginji_plan_retry_prompt.txt <<EOF_PLAN_RETRY
your last SESSION_PLAN.md was invalid.
rewrite it now using the exact required header fields and make sure verify prints one number.
keep the improvement measurable, capability-oriented, and scoped to repo paths.
EOF_PLAN_RETRY
  run_with_timeout "$TIMEOUT" "cat /tmp/ginji_plan_retry_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_plan_retry.log || true
fi

if [[ ! -s SESSION_PLAN.md ]] || ! validate_session_plan; then
  echo "planning fallback: writing default measured session plan"
  write_default_session_plan
fi

verify_command="$(session_field SESSION_PLAN.md verify 2>/dev/null || true)"
guard_command="$(session_field SESSION_PLAN.md guard 2>/dev/null || true)"
direction="$(session_field SESSION_PLAN.md direction 2>/dev/null || true)"
iteration_budget="$(session_field SESSION_PLAN.md iteration_budget 2>/dev/null || true)"
stop_condition="$(session_field SESSION_PLAN.md stop_condition 2>/dev/null || true)"
metric_name="$(session_field SESSION_PLAN.md metric 2>/dev/null || true)"
scope_text="$(session_field SESSION_PLAN.md scope 2>/dev/null || true)"

[[ -z "$verify_command" ]] && verify_command="$DEFAULT_VERIFY"
[[ -z "$guard_command" ]] && guard_command="$BUILD_CHECK"
[[ -z "$direction" ]] && direction="higher"
[[ -z "$iteration_budget" ]] && iteration_budget="3"

baseline_metric=""
if ! baseline_metric="$(measure_metric_value "$verify_command" 2>/tmp/ginji_metric_baseline.err)"; then
  echo "baseline failed, falling back to default measured session plan"
  write_default_session_plan
  verify_command="$(session_field SESSION_PLAN.md verify)"
  guard_command="$(session_field SESSION_PLAN.md guard)"
  direction="$(session_field SESSION_PLAN.md direction)"
  iteration_budget="$(session_field SESSION_PLAN.md iteration_budget)"
  stop_condition="$(session_field SESSION_PLAN.md stop_condition)"
  metric_name="$(session_field SESSION_PLAN.md metric)"
  scope_text="$(session_field SESSION_PLAN.md scope)"
  baseline_metric="$(measure_metric_value "$verify_command")"
fi

log_metric_result "$next_day" "0" "$baseline_metric" "0" "baseline" "baseline row for ${metric_name}"
best_metric="$baseline_metric"
last_keep_description="baseline"

mapfile -t scope_paths < <(parse_scope_paths "$scope_text")
if [[ "${#scope_paths[@]}" -eq 0 ]]; then
  mapfile -t scope_paths < <(parse_scope_paths "src/ginji.py, tests, scripts, skills, README.md, docs/book/evolution.md, wiki/evolution-pipeline.md, wiki/testing-and-safety.md, wiki/prompts-and-skills-system.md")
fi

echo "step 5: bounded metric loop (phase b)"
for ((iteration=1; iteration<=iteration_budget; iteration++)); do
  snapshot_dir="$(mktemp -d)"
  snapshot_scope_state "$snapshot_dir" "${scope_paths[@]}"
  cat > /tmp/ginji_impl_prompt.txt <<EOF_IMPL
you are implementing iteration ${iteration}/${iteration_budget} from SESSION_PLAN.md.
read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv before changing anything.
keep the change inside this declared scope only:
${scope_text}
current best metric for '${metric_name}': ${best_metric}
direction: ${direction}
verify command: ${verify_command}
guard command: ${guard_command}
requirements:
- make one atomic change only
- pick the next change most likely to improve the metric
- if this is the final iteration, exploit the strongest direction seen so far instead of trying a brand new angle
- do not do maintenance-only cleanup unless it directly improves the metric or prevents repeated failure in this scope
- do not rewrite SESSION_PLAN.md or EVOLUTION_RESULTS.tsv
- you may run local checks, but the harness will decide keep or discard from the metric and guard
EOF_IMPL

  if ! run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_impl_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > "/tmp/ginji_impl_${iteration}.log"; then
    restore_scope_state "$snapshot_dir"
    log_metric_result "$next_day" "$iteration" "$best_metric" "0" "crash" "iteration ${iteration} agent execution failed"
    rm -rf "$snapshot_dir"
    continue
  fi

  candidate_metric=""
  if ! candidate_metric="$(measure_metric_value "$verify_command" 2>/tmp/ginji_metric_iteration.err)"; then
    restore_scope_state "$snapshot_dir"
    log_metric_result "$next_day" "$iteration" "$best_metric" "0" "crash" "iteration ${iteration} verify command failed"
    rm -rf "$snapshot_dir"
    continue
  fi

  compare_output="$(compare_metric_values "$direction" "$best_metric" "$candidate_metric")"
  compare_status="$(printf '%s' "$compare_output" | cut -f1)"
  delta_value="$(printf '%s' "$compare_output" | cut -f2)"
  description="$(grep -m1 -v '^$' "/tmp/ginji_impl_${iteration}.log" | head -n 1 || true)"
  [[ -z "$description" ]] && description="iteration ${iteration} change inside ${scope_text}"

  if [[ "$compare_status" != "improved" ]]; then
    restore_scope_state "$snapshot_dir"
    log_metric_result "$next_day" "$iteration" "$candidate_metric" "$delta_value" "discard" "metric did not improve: ${description}"
    rm -rf "$snapshot_dir"
    continue
  fi

  if ! bash -lc "$guard_command"; then
    restore_scope_state "$snapshot_dir"
    log_metric_result "$next_day" "$iteration" "$candidate_metric" "$delta_value" "discard" "guard failed after improvement attempt: ${description}"
    rm -rf "$snapshot_dir"
    continue
  fi

  best_metric="$candidate_metric"
  last_keep_description="$description"
  log_metric_result "$next_day" "$iteration" "$candidate_metric" "$delta_value" "keep" "$description"
  rm -rf "$snapshot_dir"

  if [[ "$stop_condition" == *"first kept improvement"* ]]; then
    echo "stop condition reached after iteration ${iteration}"
    break
  fi
done

echo "step 6: extract issue responses from plan (phase c)"
cat > /tmp/ginji_issue_prompt.txt <<EOF_ISSUE
review SESSION_PLAN.md and your implementation logs.
if you worked on any github issue, write ISSUE_RESPONSE.md exactly in the communicate skill format.
if no issue work was done, do not create ISSUE_RESPONSE.md.
keep lowercase and use ginji's small silver fox voice.
EOF_ISSUE
run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_issue_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_issue_phase.log || true

echo "step 7: verify build after changes"
build_ok=0
if bash -lc "$BUILD_CHECK"; then
  build_ok=1
else
  for attempt in 1 2 3; do
    echo "build failed, auto-fix attempt ${attempt}"
    cat > /tmp/ginji_fix_prompt.txt <<EOF_FIX
build checks failed.
read the failing output and fix the smallest issue needed.
then run:
python -m py_compile src/ginji.py && python -m pytest tests/ -q
if this is attempt 3 and still stuck, stop.
EOF_FIX
    run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_fix_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > "/tmp/ginji_fix_${attempt}.log" || true
    if bash -lc "$BUILD_CHECK"; then
      build_ok=1
      break
    fi
  done
fi

if [[ "$build_ok" -ne 1 ]]; then
  echo "step 7 fallback: reverting src/ and tests/"
  git checkout -- src/ tests/ || true
  bash -lc "$BUILD_CHECK"
fi

echo "step 8: ensure journal was written"
cat > /tmp/ginji_journal_prompt.txt <<EOF_JOURNAL
read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv.
write one journal entry to JOURNAL_ENTRY.md only.
do not rewrite JOURNAL.md directly.
format exactly:
## day ${next_day} — ${now_hhmm} — [short title]

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
EOF_JOURNAL
run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_journal_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_journal.log || true
sanitize_journal_entry "JOURNAL_ENTRY.md"
if [[ -f JOURNAL_ENTRY.md ]] && ! grep -q "^## day ${next_day} —" JOURNAL_ENTRY.md; then
  cat > /tmp/ginji_journal_retry_prompt.txt <<EOF_JOURNAL_RETRY
rewrite JOURNAL_ENTRY.md for day ${next_day} in ginji's voice.
keep it lowercase, specific, and 4-6 sentences.
focus on the kept metric result from EVOLUTION_RESULTS.tsv.
do not write any files except JOURNAL_ENTRY.md.
EOF_JOURNAL_RETRY
  run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_journal_retry_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_journal_retry.log || true
  sanitize_journal_entry "JOURNAL_ENTRY.md"
fi
if [[ -f JOURNAL_ENTRY.md ]] && grep -q "^## day ${next_day} —" JOURNAL_ENTRY.md; then
  prepend_journal_entry "$next_day" "JOURNAL_ENTRY.md"
fi
if ! grep -q "^## day ${next_day} —" JOURNAL.md; then
  append_fallback_journal "$next_day" "$now_hhmm"
fi
echo "step 8c: restore missing journal history if needed"
restore_missing_journal_history "$journal_history_snapshot"
rm -f JOURNAL_ENTRY.md

echo "step 8b: ensure learnings were written"
cat > /tmp/ginji_learning_prompt.txt <<EOF_LEARNING
read SESSION_PLAN.md and EVOLUTION_RESULTS.tsv.
write one learning entry to LEARNINGS_ENTRY.md only.
do not rewrite LEARNINGS.md directly.
format exactly:
## [short topic]
**learned:** day ${next_day}
**source:** [session observation, test output, docs, or code review]
[2-4 sentences describing what moved the metric, what did not, and what that means for future sessions]
rules:
- focus on the measured loop, not generic motivation
- tie the learning to a concrete command, file, guard, or discarded attempt
- keep it lowercase
EOF_LEARNING
run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_learning_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_learning.log || true
if [[ -f LEARNINGS_ENTRY.md ]] && grep -q "^\\*\\*learned:\\*\\* day ${next_day}$" LEARNINGS_ENTRY.md; then
  prepend_learnings_entry "$next_day" "LEARNINGS_ENTRY.md"
else
  append_fallback_learning "$next_day"
fi
rm -f LEARNINGS_ENTRY.md

echo "step 9: process ISSUE_RESPONSE.md"
process_issue_responses

echo "step 10: rebuild website"
python scripts/build_site.py

echo "step 11: commit remaining changes"
rm -f "$journal_history_snapshot"
echo "$(latest_journal_day)" > DAY_COUNT
echo "$today_pst" > LAST_POST_DATE_PST
if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "day ${next_day} (${now_hhmm}): evolution session"
else
  echo "no changes to commit"
fi

echo "step 12: tag the commit"
tag_name="day${next_day}-$(date +%H-%M)"
if git rev-parse "$tag_name" >/dev/null 2>&1; then
  echo "tag already exists: ${tag_name}"
else
  git tag "$tag_name"
fi

echo "step 13: git push"
if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD || true
  git push origin "$tag_name" || true
else
  echo "no git remote configured, skipping push"
fi

echo "evolution run complete"
