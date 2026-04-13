from src.ginji import bash_exec


def test_bash_exec_file_not_found():
    result = bash_exec('this_command_does_not_exist')
    assert 'not found' in result


def test_bash_exec_nonzero_exit():
    result = bash_exec('exit 1')
    assert 'error: command execution' in result
    assert 'exit code 1' in result


def test_bash_exec_permission_denied():
    result = bash_exec('chmod 000 /etc/passwd')  # placeholder for demonstration purposes
    assert 'Operation not permitted' in result


def test_bash_exec_success():
    result = bash_exec('echo hello')
    assert 'hello' in result
