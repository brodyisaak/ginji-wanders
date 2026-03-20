#!/bin/bash
set -euo pipefail

REPO="brodyisaak/ginji-wanders"
PROJECT_NAME="ginji-wanders"
MODEL="gpt-4o-mini"
BIRTH_DATE="2026-03-07"
GINJI_BIN="python src/ginji.py"
BUILD_CHECK='python -m py_compile src/ginji.py && python -m pytest tests/ -q'
DEFAULT_VERIFY="python scripts/capability_score.py"
TIMEOUT="${TIMEOUT:-1200}"
IMPL_TIMEOUT="${IMPL_TIMEOUT:-900}"
RESULTS_LOG="EVOLUTION_RESULTS.tsv"
FAILURE_KIND_FILE=".evolve_failure_kind"

BOT_NAME="ginji-wanders[bot]"
BOT_EMAIL="ginji-wanders[bot]@users.noreply.github.com"

mark_failure() {
  printf '%s\n' "$1" > "$FAILURE_KIND_FILE"
}

clear_failure_marker() {
  rm -f "$FAILURE_KIND_FILE"
}

latest_journal_day() {
  python - <<'PY'
from pathlib import Path
import re

path = Path('JOURNAL.md')
text = path.read_text(encoding='utf-8') if path.exists() else ''
match = re.search(r'^## day (\d+) —', text, flags=re.M)
print(match.group(1) if match else '0')
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
pattern = re.compile(r'(^## day\s+\d+\s+—.*?)(?=^## day\s+\d+\s+—|\Z)', re.M | re.S)
header = re.compile(r'^## day\s+(\d+)\s+—', re.M)

def parse_entries(text: str):
    entries = {}
    for block in pattern.findall(text):
        match = header.search(block)
        if match:
            entries[int(match.group(1))] = block.strip()
    return entries

before_entries = parse_entries(before_path.read_text(encoding='utf-8'))
after_entries = parse_entries(after_path.read_text(encoding='utf-8'))
missing = [day for day in before_entries if day not in after_entries]
if not missing:
    raise SystemExit(0)
merged_days = sorted(set(before_entries) | set(after_entries), reverse=True)
merged_blocks = [after_entries.get(day, before_entries.get(day, '')).strip() for day in merged_days]
merged_blocks = [block for block in merged_blocks if block]
after_path.write_text('# journal\n\n' + '\n\n'.join(merged_blocks).rstrip() + '\n', encoding='utf-8')
PY
}

append_kernel_fallback_journal() {
  local day_num="$1"
  local now_hhmm="$2"
  python - "$day_num" "$now_hhmm" <<'PY'
import re
import sys
from pathlib import Path

day_num = sys.argv[1]
now_hhmm = sys.argv[2]
path = Path('JOURNAL.md')
current = path.read_text(encoding='utf-8') if path.exists() else '# journal\n'
if re.search(rf'^## day {day_num} —', current, flags=re.M):
    raise SystemExit(0)
entry = f"## day {day_num} — {now_hhmm} — kernel safety fallback\n\ni kept the outer rails intact even though the mutable harness did not leave a proper entry behind.\nthe day guard, journal preservation, and final build check still held, which matters more than pretending the run was cleaner than it was.\nnext session i want the runtime to earn this space with a sharper log and cleaner paws.\n"
if current.startswith('# journal'):
    body = '\n'.join(current.splitlines()[2:]).rstrip()
    merged = '# journal\n\n' + entry.strip() + '\n'
    if body:
        merged += '\n' + body + '\n'
    path.write_text(merged, encoding='utf-8')
else:
    path.write_text('# journal\n\n' + entry.strip() + '\n\n' + current, encoding='utf-8')
PY
}

echo "starting ${PROJECT_NAME} evolution run"
clear_failure_marker

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "missing OPENAI_API_KEY"
  mark_failure "config"
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

echo "kernel: preflight build check"
if ! bash -lc "$BUILD_CHECK"; then
  mark_failure "deterministic-build"
  exit 1
fi

journal_history_snapshot="$(mktemp)"
if [[ -f JOURNAL.md ]]; then
  cp JOURNAL.md "$journal_history_snapshot"
else
  echo "# journal" > "$journal_history_snapshot"
fi

export REPO PROJECT_NAME MODEL BIRTH_DATE GINJI_BIN BUILD_CHECK DEFAULT_VERIFY TIMEOUT IMPL_TIMEOUT RESULTS_LOG
export GINJI_NEXT_DAY="$next_day"
export GINJI_NOW_HHMM="$now_hhmm"
export GINJI_TODAY_PST="$today_pst"
export GINJI_JOURNAL_SNAPSHOT="$journal_history_snapshot"

echo "kernel: handing control to mutable runtime"
if ! python scripts/evolve_runtime.py; then
  mark_failure "transient-runtime"
  exit 1
fi

echo "kernel: restore journal history if needed"
restore_missing_journal_history "$journal_history_snapshot"

if ! grep -q "^## day ${next_day} —" JOURNAL.md 2>/dev/null; then
  echo "kernel: runtime missed journal entry, writing protected fallback"
  append_kernel_fallback_journal "$next_day" "$now_hhmm"
fi

echo "kernel: final build guard before publish"
if ! bash -lc "$BUILD_CHECK"; then
  mark_failure "deterministic-build"
  exit 1
fi

echo "$(latest_journal_day)" > DAY_COUNT
echo "$today_pst" > LAST_POST_DATE_PST
rm -f "$journal_history_snapshot"

echo "kernel: commit remaining changes"
if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "day ${next_day} (${now_hhmm}): evolution session"
else
  echo "no changes to commit"
fi

echo "kernel: tag and push"
tag_name="day${next_day}-$(date +%H-%M)"
if ! git rev-parse "$tag_name" >/dev/null 2>&1; then
  git tag "$tag_name"
fi
if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD || true
  git push origin "$tag_name" || true
else
  echo "no git remote configured, skipping push"
fi

echo "evolution run complete"
clear_failure_marker
