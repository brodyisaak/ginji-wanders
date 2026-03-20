from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capability_score", ROOT / "scripts" / "capability_score.py")
capability_score = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(capability_score)


def test_dimension_counts_and_score():
    passed = [
        "tests/test_ginji.py::test_bash_exec_success",
        "tests/test_ginji.py::test_bash_exec_file_not_found",
        "tests/test_ginji.py::test_bash_exec_permission_denied",
        "tests/test_ginji.py::test_list_files_success",
        "tests/test_ginji.py::test_list_files_nested_paths",
        "tests/test_ginji.py::test_search_files_matches",
        "tests/test_ginji.py::test_search_files_no_matches",
        "tests/test_ginji.py::test_search_files_regex_matches_multiple_files",
    ]
    counts = capability_score.dimension_counts(passed)
    assert counts["exec"] == 3
    assert counts["nav"] == 2
    assert counts["search"] == 3
    assert capability_score.score_from_counts(counts) == 16


def test_gap_report_sorts_highest_available_gain_first():
    counts = {
        "git": 0,
        "recovery": 3,
        "edit": 4,
        "exec": 3,
        "nav": 2,
        "search": 2,
        "harness": 3,
    }
    gaps = capability_score.gap_report(counts)
    assert gaps[0]["dimension"] == "git"
    assert gaps[0]["available_gain"] == 12
    search_gap = next(gap for gap in gaps if gap["dimension"] == "search")
    nav_gap = next(gap for gap in gaps if gap["dimension"] == "nav")
    assert search_gap["available_gain"] == 2
    assert nav_gap["available_gain"] == 2
