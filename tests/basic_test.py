import subprocess

def test_bash_exec_functionality():
    command = "echo hello"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Command: {command}")
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    assert result.returncode == 0
    assert "hello" in result.stdout