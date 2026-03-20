import subprocess

def test_invalid_git_command():
    command = "git non_existing_command"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Running command: {command}")
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    assert result.returncode != 0
    assert "not a git command" in result.stderr.lower()