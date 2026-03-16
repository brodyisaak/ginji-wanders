import pytest
from pathlib import Path
from src.ginji import bash_exec, read_file, write_file, edit_file, list_files, search_files


# bash_exec

@pytest.mark.capability("exec")
def test_bash_exec_file_not_found():
    output = bash_exec('non_existing_command')
    assert 'not found' in output


@pytest.mark.capability("exec")
def test_bash_exec_permission_denied():
    output = bash_exec('command_without_permit')
    assert 'not found' in output


@pytest.mark.capability("exec")
def test_bash_exec_success():
    output = bash_exec('echo hello')
    assert 'hello' in output


@pytest.mark.capability("recovery")
def test_bash_exec_nonzero_exit():
    output = bash_exec('exit 1')
    assert output.startswith('error:')


# read_file

@pytest.mark.capability("recovery")
def test_read_file_not_found():
    output = read_file('/nonexistent/path/file.txt')
    assert output.startswith('error:')


@pytest.mark.capability("nav")
def test_read_file_success(tmp_path):
    f = tmp_path / 'hello.txt'
    f.write_text('hello world', encoding='utf-8')
    assert read_file(str(f)) == 'hello world'


# write_file

@pytest.mark.capability("edit")
def test_write_file_success(tmp_path):
    path = str(tmp_path / 'out.txt')
    result = write_file(path, 'content')
    assert result.startswith('ok:')
    assert Path(path).read_text(encoding='utf-8') == 'content'


@pytest.mark.capability("edit")
def test_write_file_creates_dirs(tmp_path):
    path = str(tmp_path / 'a' / 'b' / 'out.txt')
    result = write_file(path, 'nested')
    assert result.startswith('ok:')
    assert Path(path).exists()


# edit_file

@pytest.mark.capability("edit")
def test_edit_file_success(tmp_path):
    f = tmp_path / 'edit.txt'
    f.write_text('foo bar', encoding='utf-8')
    result = edit_file(str(f), 'foo', 'baz')
    assert result.startswith('ok:')
    assert f.read_text(encoding='utf-8') == 'baz bar'


@pytest.mark.capability("recovery")
def test_edit_file_old_str_not_found(tmp_path):
    f = tmp_path / 'edit.txt'
    f.write_text('foo bar', encoding='utf-8')
    result = edit_file(str(f), 'missing', 'new')
    assert result.startswith('error:')


@pytest.mark.capability("edit")
def test_edit_file_replaces_first_occurrence_only(tmp_path):
    f = tmp_path / 'edit.txt'
    f.write_text('ab ab ab', encoding='utf-8')
    edit_file(str(f), 'ab', 'x')
    assert f.read_text(encoding='utf-8') == 'x ab ab'


# list_files

@pytest.mark.capability("nav")
def test_list_files_success(tmp_path):
    (tmp_path / 'a.txt').write_text('', encoding='utf-8')
    (tmp_path / 'b.txt').write_text('', encoding='utf-8')
    output = list_files(str(tmp_path))
    assert 'a.txt' in output
    assert 'b.txt' in output


@pytest.mark.capability("recovery")
def test_list_files_not_found():
    output = list_files('/nonexistent/directory')
    assert output.startswith('error:')


# search_files

@pytest.mark.capability("search")
def test_search_files_matches(tmp_path):
    f = tmp_path / 'code.py'
    f.write_text('def hello():\n    pass\n', encoding='utf-8')
    output = search_files('hello', str(tmp_path))
    assert 'hello' in output


@pytest.mark.capability("search")
def test_search_files_no_matches(tmp_path):
    f = tmp_path / 'code.py'
    f.write_text('nothing here', encoding='utf-8')
    output = search_files('xyz_not_there', str(tmp_path))
    assert output == 'no matches found.'


@pytest.mark.capability("recovery")
def test_search_files_directory_not_found():
    output = search_files('anything', '/nonexistent/directory')
    assert output.startswith('error:')
