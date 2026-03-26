#!/usr/bin/env python3
import argparse
import json
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
    "test_list_files_nested_paths": "nav",
    "test_list_files_not_found": "recovery",
    "test_search_files_matches": "search",
    "test_search_files_no_matches": "search",
    "test_search_files_regex_matches_multiple_files": "search",
    "test_search_files_directory_not_found": "recovery",
    "test_git_init_temp_repo": "git",
    "test_git_status_temp_repo": "git",
    "test_git_invalid_command_reports_git_error": "git",
    "test_git_commit_temp_repo": "git",
}

REQUIRED_TESTS = {
    "git": {
        "test_git_init_temp_repo",
        "test_git_status_temp_repo",
        "test_git_invalid_command_reports_git_error",
        "test_git_commit_temp_repo",
    },
    "recovery": {
        "test_bash_exec_nonzero_exit",
        "test_read_file_not_found",
        "test_edit_file_old_str_not_found",
        "test_list_files_not_found",
        "test_search_files_directory_not_found",
    },
    "edit": {
        "test_write_file_success",
        "test_write_file_creates_dirs",
        "test_edit_file_success",
        "test_edit_file_replaces_first_occurrence_only",
    },
    "exec": {
        "test_bash_exec_file_not_found",
        "test_bash_exec_permission_denied",
        "test_bash_exec_success",
    },
    "nav": {
        "test_read_file_success",
        "test_list_files_success",
        "test_list_files_nested_paths",
    },
    "search": {
        "test_search_files_matches",
        "test_search_files_no_matches",
        "test_search_files_regex_matches_multiple_files",
    },
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

COMPLETENESS_BONUS = {
    "git": 2,
    "recovery": 2,
    "edit": 2,
    "exec": 1,
    "nav": 1,
    "search": 1,
    "harness": 0,
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


def passed_test_nodes(pytest_output):
    nodes = []
    for line in pytest_output.splitlines():
        match = PASSED_LINE.search(line.strip())
        if match:
            nodes.append(match.group(1))
    return nodes


def dimension_counts(passed_names):
    counts = {name: 0 for name in WEIGHTS}
    for node_id in passed_names:
        dimension = dimension_for_test(node_id)
        if dimension is not None:
            counts[dimension] += 1
    return counts


def score_from_counts(counts):
    score = 0
    for dimension, weight in WEIGHTS.items():
        score += weight * min(counts[dimension], CAP)
    score += completeness_bonus(counts)
    return score


def completeness_bonus(counts):
    bonus = 0
    for dimension, required_tests in REQUIRED_TESTS.items():
        if counts.get(dimension, 0) >= len(required_tests):
            bonus += COMPLETENESS_BONUS.get(dimension, 0)
    return bonus


def gap_report(counts):
    gaps = []
    for dimension, weight in WEIGHTS.items():
        counted = min(counts[dimension], CAP)
        remaining = max(CAP - counted, 0)
        gaps.append(
            {
                "dimension": dimension,
                "count": counts[dimension],
                "counted": counted,
                "remaining": remaining,
                "weight": weight,
                "available_gain": remaining * weight,
                "completeness_bonus": COMPLETENESS_BONUS.get(dimension, 0),
                "complete": counts[dimension] >= len(REQUIRED_TESTS.get(dimension, set())),
            }
        )
    gaps.sort(key=lambda item: (item["available_gain"], item["weight"], item["dimension"]), reverse=True)
    return gaps


def run_pytest(args):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = (result.stderr or "").strip() or (result.stdout or "").strip() or "error: pytest failed to run"
        print(message, file=sys.stderr)
        return 1, []

    passed_names = passed_test_nodes(result.stdout)

    if not passed_names:
        fallback = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-vv", "--tb=no"],
            capture_output=True,
            text=True,
        )
        if fallback.returncode != 0:
            message = (fallback.stderr or "").strip() or (fallback.stdout or "").strip() or "error: pytest failed to run"
            print(message, file=sys.stderr)
            return 1, []
        passed_names = passed_test_nodes(fallback.stdout)

    return 0, passed_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    code, passed_names = run_pytest(args)
    if code != 0:
        return code

    counts = dimension_counts(passed_names)
    score = score_from_counts(counts)

    if args.details:
        payload = {
            "score": score,
            "base_score": sum(weight * min(counts[dimension], CAP) for dimension, weight in WEIGHTS.items()),
            "completeness_bonus": completeness_bonus(counts),
            "counts": counts,
            "gaps": gap_report(counts),
        }
        print(json.dumps(payload, separators=(",", ":")))
        return 0

    print(score)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
