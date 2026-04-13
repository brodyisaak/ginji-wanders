import os
import tempfile
import pytest
from src.ginji import bash_exec, read_file, write_file, edit_file, list_files


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


def test_write_file_success():
    path = 'test/temp_write_file.txt'
    content = 'hello world!'
    write_file(path, content)
    assert os.path.exists(path)
    os.remove(path)


def test_read_file_success():
    path = 'test/temp_read_file.txt'
    content = 'hello again!'
    write_file(path, content)
    assert read_file(path) == content
    os.remove(path)


def test_edit_file_success():
    path = 'test/temp_edit_file.txt'
    old_content = 'change this'
    new_content = 'changed!'
    write_file(path, old_content)
    edit_file(path, old_content, new_content)
    assert read_file(path) == new_content
    os.remove(path)


def test_list_files_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, 'test_list_file.txt')
        write_file(path, 'some content')
        files = list_files(temp_dir)
        assert os.path.basename(path) in files
        os.remove(path)  # Clean up
