from pathlib import Path
import importlib.util
import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("metric_guard", ROOT / "scripts" / "metric_guard.py")
metric_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(metric_guard)


def test_parse_metric_integer():
    assert metric_guard.parse_metric("score: 12\n") == 12.0


def test_parse_metric_float():
    assert metric_guard.parse_metric("metric: 4.25\n") == 4.25


def test_parse_metric_rejects_non_numeric():
    with pytest.raises(ValueError):
        metric_guard.parse_metric("no usable number here\n")


def test_measure_command_rejects_failed_command():
    with pytest.raises(RuntimeError):
        metric_guard.measure_command("python -c 'import sys; sys.exit(1)'")
