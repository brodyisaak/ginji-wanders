import pytest
from src.ginji import list_files


def test_list_files_success(tmp_path):
    (tmp_path / 'sample.txt').write_text('content here')
    output = list_files(str(tmp_path))
    assert 'sample.txt' in output

def test_list_files_no_files(tmp_path):
    output = list_files(str(tmp_path))
    assert 'no files found.' in output
