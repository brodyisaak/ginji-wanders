import subprocess

import pytest

from src.ginji import bash_exec


def init_temp_repo(tmp_path):
    path = tmp_path / "test_repo"
    path.mkdir()
    result = subprocess.run(["git", "init", str(path)], capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=path, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, capture_output=True, text=True, check=True)
    return path, (result.stdout or "") + (result.stderr or "")


@pytest.mark.capability("git")
def test_git_init_temp_repo(tmp_path):
    _path, output = init_temp_repo(tmp_path)
    assert "initialized empty git repository" in output.lower()


@pytest.mark.capability("git")
def test_git_status_temp_repo(tmp_path):
    path, _output = init_temp_repo(tmp_path)
    result = subprocess.run(["git", "status"], cwd=path, capture_output=True, text=True, check=True)
    output = (result.stdout or "") + (result.stderr or "")
    assert "on branch" in output.lower()
    assert "no commits yet" in output.lower()


@pytest.mark.capability("git")
def test_git_invalid_command_reports_git_error():
    output = bash_exec("git non_existing_command")
    assert output.startswith("error:")
    assert "not a git command" in output.lower()


@pytest.mark.capability("git")
def test_git_commit_temp_repo(tmp_path):
    path, _output = init_temp_repo(tmp_path)
    (path / "file.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True, text=True, check=True)
    result = subprocess.run(["git", "commit", "-m", "test commit"], cwd=path, capture_output=True, text=True, check=True)
    output = (result.stdout or "") + (result.stderr or "")
    assert "test commit" in output
