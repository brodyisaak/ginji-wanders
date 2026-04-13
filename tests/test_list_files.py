import os
import tempfile
from src.ginji import list_files, write_file


def test_list_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, 'test_list_file.txt')
        write_file(path, 'some content')
        files = list_files(temp_dir)
        assert os.path.basename(path) in files
        os.remove(path)  # Ensure the created file is cleaned up
