import pytest
from src.ginji import bash_exec


def test_bash_exec_success():
    output = bash_exec('echo hello')
    assert 'hello' in output