#!/usr/bin/env python3
import re
import subprocess
import sys


TEST_TO_DIMENSION = {
    "test_bash_exec_file_not_found": "exec",
    "test_bash_exec_permission_denied": "exec",
    "test_bash_exec_success": "exec",
    "test_bash_exec_nonzero_exit": "recovery",
    "test_read_file_not_found": "recovery",
    "test_read_file_success": "nav",
    "test_write_file_success": "edit",
    "test_write_file_creates_dirs": "edit",
    "test_edit_file_success": "edit",
    "test_edit_file_old_str_not_found": "recovery",
    "test_edit_file_replaces_first_occurrence_only": "edit",
    "test_list_files_success": "nav",
    "test_list_files_not_found": "recovery",
    "test_search_files_matches": "search",
    "test_search_files_no_matches": "search",
    "test_search_files_directory_not_found": "recovery",
}

WEIGHTS = {
    "git": 4,
    "recovery": 3,
    "edit": 3,
    "exec": 2,
    "nav": 2,
    "search": 2,
    "harness": 1,
}

CAP = 3
PASSED_LINE = re.compile(r"^(\S+)\s+PASSED(?:\s|\[|$)")


def dimension_for_test(node_id):
    if "tests/test_repo_integrity.py::" in node_id or "tests/test_metric_guard.py::" in node_id:
        return "harness"
    test_name = node_id.rsplit("::", 1)[-1]
    if test_name in TEST_TO_DIMENSION:
        return TEST_TO_DIMENSION[test_name]
    return None


def main():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = (result.stderr or "").strip() or (result.stdout or "").strip() or "error: pytest failed to run"
        print(message, file=sys.stderr)
        return 1

    passed_names = []
    for line in result.stdout.splitlines():
        match = PASSED_LINE.search(line.strip())
        if not match:
            continue
        passed_names.append(match.group(1))

    if not passed_names:
        fallback = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-vv", "--tb=no"],
            capture_output=True,
            text=True,
        )
        if fallback.returncode != 0:
            message = (fallback.stderr or "").strip() or (fallback.stdout or "").strip() or "error: pytest failed to run"
            print(message, file=sys.stderr)
            return 1
        for line in fallback.stdout.splitlines():
            match = PASSED_LINE.search(line.strip())
            if not match:
                continue
            passed_names.append(match.group(1))

    counts = {name: 0 for name in WEIGHTS}
    for node_id in passed_names:
        dimension = dimension_for_test(node_id)
        if dimension is not None:
            counts[dimension] += 1

    score = 0
    for dimension, weight in WEIGHTS.items():
        score += weight * min(counts[dimension], CAP)

    print(score)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
