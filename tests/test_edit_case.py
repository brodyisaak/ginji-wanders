import pytest
from src.ginji import edit_file

def test_edit_file():
    # Arrange
    test_file_path = 'simple_test_case.txt'
    with open(test_file_path, 'w') as f:
        f.write('Old Text')
    
    # Act
    result = edit_file(test_file_path, 'Old Text', 'New Text')
    
    # Assert
    assert result == 'ok: wrote simple_test_case.txt'
    with open(test_file_path, 'r') as f:
        assert f.read() == 'New Text'


def test_edit_file_no_old_str():
    # Arrange
    test_file_path = 'simple_test_case.txt'
    with open(test_file_path, 'w') as f:
        f.write('Old Text')
    
    # Act
    result = edit_file(test_file_path, 'Nonexistent', 'Replacement')
    
    # Assert
    assert result == 'error: old_str not found in file'