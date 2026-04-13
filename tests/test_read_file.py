import os
from src.ginji import read_file, write_file


def test_read_file_success():
    path = 'test/temp_read_file.txt'
    content = 'hello again!'
    write_file(path, content)
    result = read_file(path)
    assert result == content
    # Clean up
    os.remove(path)
