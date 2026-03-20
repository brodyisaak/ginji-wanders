import subprocess

def init_temp_repo(tmp_path):
    path = tmp_path / "test_repo"
    path.mkdir()
    result = subprocess.run(["git", "init", str(path)], capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=path, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, capture_output=True, text=True, check=True)
    return path, (result.stdout or "") + (result.stderr or "")


def test_git_commit_temp_repo(tmp_path):
    print('running commit test...')
    path, _output = init_temp_repo(tmp_path)
    (path / "file.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True, text=True, check=True)
    result = subprocess.run(["git", "commit", "-m", "test commit"], cwd=path, capture_output=True, text=True, check=True)
    output = (result.stdout or "") + (result.stderr or "")
    print(f"Output from commit: {output}")
    assert "test commit" in output