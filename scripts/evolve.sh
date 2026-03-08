#!/bin/bash
set -euo pipefail

REPO="brodyisaak/ginji-wanders"
PROJECT_NAME="ginji-wanders"
MODEL="gpt-4o-mini"
BIRTH_DATE="2026-03-07"
GINJI_BIN="python src/ginji.py"
BUILD_CHECK='python -m py_compile src/ginji.py && python -m pytest tests/ -q'
TIMEOUT="${TIMEOUT:-1200}"
IMPL_TIMEOUT="${IMPL_TIMEOUT:-900}"

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

append_fallback_journal() {
  local day_num="$1"
  local now_hhmm="$2"
  local tmp
  tmp="$(mktemp)"
  {
    echo "# journal"
    echo
    echo "## day ${day_num} — ${now_hhmm} — fallback session log"
    echo
    echo "i ran an evolution session and validated the build."
    echo "the scripted path completed, but no explicit journal entry was written by the agent."
    echo "tests are green and the site was rebuilt."
    echo "next i should make one sharper improvement and document it directly."
    echo
    tail -n +2 JOURNAL.md
  } > "$tmp"
  mv "$tmp" JOURNAL.md
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
now_hhmm="$(date +%H:%M)"

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
cat > /tmp/ginji_plan_prompt.txt <<EOF
you are ginji, a self-evolving coding agent.
this is day ${next_day} (born ${BIRTH_DATE}).
read these files before planning:
- IDENTITY.md
- PERSONALITY.md
- src/ginji.py
- JOURNAL.md
- LEARNINGS.md
- ISSUES_TODAY.md
then run this command:
python -m pytest tests/ -q
write SESSION_PLAN.md content in lowercase where appropriate.
choose one improvement only for this session.
include: objective, scope, tests to run, risk notes, and up to five concrete tasks.
EOF

run_with_timeout "$TIMEOUT" "cat /tmp/ginji_plan_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > SESSION_PLAN.md || true
if [[ ! -s SESSION_PLAN.md ]]; then
  echo "session plan generation failed." > SESSION_PLAN.md
fi

echo "step 5: implementation loop (phase b)"
for task_num in 1 2 3 4 5; do
  cat > /tmp/ginji_impl_prompt.txt <<EOF
you are implementing phase b task ${task_num} from SESSION_PLAN.md.
python-specific work only.
execute one next unfinished task from SESSION_PLAN.md.
after changes, run:
python -m py_compile src/ginji.py && python -m pytest tests/ -q
if stuck after 3 attempts revert with:
git checkout -- src/ tests/
commit format when committing task work:
git add -A && git commit -m 'day ${next_day} (${now_hhmm}): [title] (task ${task_num})'
if no unfinished tasks remain, respond exactly: no tasks left.
EOF
  run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_impl_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > "/tmp/ginji_impl_${task_num}.log" || true
  if grep -qi "^no tasks left\.$" "/tmp/ginji_impl_${task_num}.log"; then
    echo "implementation complete before task ${task_num}"
    break
  fi
done

echo "step 6: extract issue responses from plan (phase c)"
cat > /tmp/ginji_issue_prompt.txt <<EOF
review SESSION_PLAN.md and your implementation logs.
if you worked on any github issue, write ISSUE_RESPONSE.md exactly in the communicate skill format.
if no issue work was done, do not create ISSUE_RESPONSE.md.
keep lowercase where appropriate.
EOF
run_with_timeout "$IMPL_TIMEOUT" "cat /tmp/ginji_issue_prompt.txt | $GINJI_BIN --model '$MODEL' --skills skills" > /tmp/ginji_issue_phase.log || true

echo "step 7: verify build after changes"
build_ok=0
if bash -lc "$BUILD_CHECK"; then
  build_ok=1
else
  for attempt in 1 2 3; do
    echo "build failed, auto-fix attempt ${attempt}"
    cat > /tmp/ginji_fix_prompt.txt <<EOF
build checks failed.
read the failing output and fix the smallest issue needed.
then run:
python -m py_compile src/ginji.py && python -m pytest tests/ -q
if this is attempt 3 and still stuck, stop.
EOF
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
if ! grep -q "^## day ${next_day} —" JOURNAL.md; then
  append_fallback_journal "$next_day" "$now_hhmm"
fi

echo "step 9: process ISSUE_RESPONSE.md"
process_issue_responses

echo "step 10: rebuild website"
python scripts/build_site.py

echo "step 11: commit remaining changes"
echo "$next_day" > DAY_COUNT
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
