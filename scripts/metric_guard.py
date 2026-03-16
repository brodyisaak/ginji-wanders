#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys


NUMBER_LINE = re.compile(r"^\s*[-+]?\d+(?:\.\d+)?\s*$")
LABELED_NUMBER = re.compile(r"(?:score|metric|value)\s*[:=]\s*([-+]?\d+(?:\.\d+)?)", re.IGNORECASE)
ANY_NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?")


def parse_metric(output: str) -> float:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if NUMBER_LINE.fullmatch(line):
            return float(line)
        labeled = LABELED_NUMBER.search(line)
        if labeled:
            return float(labeled.group(1))
        numbers = ANY_NUMBER.findall(line)
        if len(numbers) == 1:
            return float(numbers[0])
    raise ValueError("could not extract a numeric metric from command output")


def measure_command(command: str) -> tuple[float, str]:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise RuntimeError(f"command failed with exit code {result.returncode}")
    return parse_metric(output), output


def compare_metrics(baseline: float, candidate: float, direction: str) -> tuple[str, float]:
    normalized = direction.strip().lower()
    if normalized not in {"higher", "lower"}:
        raise ValueError("direction must be 'higher' or 'lower'")
    delta = candidate - baseline
    if normalized == "higher":
        status = "improved" if candidate > baseline else "equal" if candidate == baseline else "worse"
    else:
        status = "improved" if candidate < baseline else "equal" if candidate == baseline else "worse"
    return status, delta


def main() -> int:
    parser = argparse.ArgumentParser(description="measure and compare evolution metrics")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    measure_parser = subparsers.add_parser("measure")
    measure_parser.add_argument("--command", required=True)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--direction", required=True)
    compare_parser.add_argument("--baseline", required=True, type=float)
    compare_parser.add_argument("--candidate", required=True, type=float)

    args = parser.parse_args()

    try:
        if args.command_name == "measure":
            metric, _ = measure_command(args.command)
            print(metric)
            return 0

        status, delta = compare_metrics(args.baseline, args.candidate, args.direction)
        print(f"{status}\t{delta}")
        return 0
    except Exception as exc:  # pragma: no cover - cli error path
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
