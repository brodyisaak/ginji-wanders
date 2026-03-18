import subprocess

import pytest

from src.ginji import bash_exec


@pytest.mark.capability("git")
def test_git_status():
    output = bash_exec('git status')
    assert 'on branch' in output.lower() or 'head detached' in output.lower()


@pytest.mark.capability("git")
def test_git_commit(tmp_path):
    path = tmp_path / 'test_repo'
    path.mkdir()
    subprocess.run(['git', 'init', str(path)], capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(path), capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(path), capture_output=True)
    (path / 'file.txt').write_text('hello', encoding='utf-8')
    subprocess.run(['git', 'add', '.'], cwd=str(path), capture_output=True)
    result = subprocess.run(['git', 'commit', '-m', 'test commit'], cwd=str(path), capture_output=True, text=True)
    assert result.returncode == 0
    assert 'test commit' in result.stdout or 'test commit' in result.stderr
