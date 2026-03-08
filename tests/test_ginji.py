from src.ginji import bash_exec

def test_bash_exec_file_not_found():
    output = bash_exec('non_existing_command')
    assert 'not found' in output


def test_bash_exec_permission_denied():
    output = bash_exec('command_without_permit')
    assert 'not found' in output