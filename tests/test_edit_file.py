import os
from src.ginji import edit_file, write_file, read_file


def test_edit_file_success():
    path = 'test/temp_edit_file.txt'
    old_content = 'change this'
    new_content = 'changed!'
    write_file(path, old_content)
    edit_file(path, old_content, new_content)
    result = read_file(path)
    assert result == new_content
    # Clean up
    os.remove(path)
