from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("evolve_runtime", ROOT / "scripts" / "evolve_runtime.py")
evolve_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(evolve_runtime)


def test_normalize_results_rows_salvages_extra_columns():
    text = "\n".join(
        [
            evolve_runtime.RESULTS_HEADER.strip(),
            "2026-03-16T07:03:51+00:00\t12\t0\t35.0\t0\tpartial\tadded a new test\t0\tbaseline\tbaseline row for git workflow tests passing",
            "2026-03-17T12:41:36+00:00\t13\t0\t35.0\t0\tbaseline\tbaseline row for git",
        ]
    )

    rows = evolve_runtime.normalize_results_rows(text)

    assert len(rows) == 2
    assert rows[0]["status"] == "partial"
    assert rows[0]["description"] == "added a new test 0 baseline baseline row for git workflow tests passing"
    assert rows[1]["status"] == "baseline"


def test_extract_iteration_description_skips_tool_noise():
    log_text = "\n".join(
        [
            "\u001b[95mtool read_file\u001b[0m",
            "# who i am",
            "",
            "added isolated temp-repo git commit coverage",
        ]
    )

    description = evolve_runtime.extract_iteration_description(
        log_text,
        iteration=2,
        scope_text="tests/test_git_workflow_tests.py",
    )

    assert description == "added isolated temp-repo git commit coverage"


def test_canonicalize_result_description_rewrites_tool_noise():
    assert (
        evolve_runtime.canonicalize_result_description("metric did not improve: \u001b[95mtool read_file\u001b[0m")
        == "metric did not improve: implementation log was noisy"
    )


def test_recent_stall_signal_prefers_live_snapshot_when_history_is_stale(tmp_path):
    results = tmp_path / "EVOLUTION_RESULTS.tsv"
    results.write_text(
        "\n".join(
            [
                evolve_runtime.RESULTS_HEADER.strip(),
                "2026-03-26T18:49:06+00:00\t22\t0\t15.0\t0\tbaseline\tbaseline row for score",
                "2026-03-26T18:49:54+00:00\t22\t1\t15.0\t0.0\tdiscard\tmetric did not improve: implementation log was noisy",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    signal = evolve_runtime.recent_stall_signal({"score": 51}, results)

    assert "recent public memory is stale" in signal
    assert "51.0" in signal
    assert "15.0" in signal
