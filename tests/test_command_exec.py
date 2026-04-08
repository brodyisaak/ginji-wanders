import pytest
from src.ginji import bash_exec

def test_command_execution():
    output = bash_exec('echo hello from bash_exec')
    print(output)  # to see the command output
    assert 'hello from bash_exec' in output