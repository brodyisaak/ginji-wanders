#!/bin/bash
# scripts/evolve-local.sh — Run evolution locally in an isolated worktree.
#
# Usage:
#   ANTHROPIC_API_KEY=sk-... ./scripts/evolve-local.sh
#
# This runs the real evolve.sh but inside a git worktree so nothing
# touches your main branch. DAY_COUNT, JOURNAL.md, commits — all isolated.

set -euo pipefail

DAY=$(cat DAY_COUNT 2>/dev/null || echo 1)
WORKTREE_DIR=".worktrees/local-day-${DAY}"
BRANCH="local-test-day-${DAY}-$(date +%s)"

echo "=== Local Evolution Test ==="
echo "Day: $DAY"
echo "Worktree: $WORKTREE_DIR"
echo "Branch: $BRANCH"
echo ""

# Clean up previous worktree at same path if it exists
if [ -d "$WORKTREE_DIR" ]; then
    echo "→ Removing previous worktree at $WORKTREE_DIR..."
    git worktree remove --force "$WORKTREE_DIR" 2>/dev/null || rm -rf "$WORKTREE_DIR"
fi

# Create worktree
echo "→ Creating isolated worktree..."
mkdir -p .worktrees
git worktree add "$WORKTREE_DIR" -b "$BRANCH" HEAD
echo "  Done."
echo ""

# Run evolve.sh inside the worktree with a fake REPO so gh commands are no-ops
echo "→ Running evolution in worktree..."
echo ""
cd "$WORKTREE_DIR"
REPO="local/test" ./scripts/evolve.sh
cd - > /dev/null

echo ""
echo "=== Local run complete ==="
echo ""
echo "Worktree: $WORKTREE_DIR"
echo "Branch:   $BRANCH"
echo ""
echo "Inspect results:"
echo "  cd $WORKTREE_DIR && git log --oneline"
echo "  cat $WORKTREE_DIR/JOURNAL.md"
echo "  cat $WORKTREE_DIR/src/main.rs"
echo ""
echo "Clean up when done:"
echo "  git worktree remove $WORKTREE_DIR && git branch -D $BRANCH"
