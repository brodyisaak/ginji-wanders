import pytest
from src.ginji import bash_exec


def test_bash_exec_logging():
    print('running test for bash_exec logging')
    output = bash_exec('exit 1')
    print(output)  # to see the command output
    assert output.startswith('error:')