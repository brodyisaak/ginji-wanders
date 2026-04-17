import pytest
from src.ginji import edit_file

def test_edit_file_success():
    # Arrange
    test_file_path = 'test.txt'
    with open(test_file_path, 'w') as f:
        f.write('Hello World')
    
    # Act
    result = edit_file(test_file_path, 'World', 'Everyone')
    
    # Assert
    assert result == 'ok: wrote test.txt'
    with open(test_file_path, 'r') as f:
        assert f.read() == 'Hello Everyone'


def test_edit_file_non_existing():
    # Arrange
    test_file_path = 'non_existing.txt'
    
    # Act
    result = edit_file(test_file_path, 'Dummy', 'Replacement')
    
    # Assert
    assert result.startswith('error:')


def test_edit_file_old_str_not_found():
    # Arrange
    test_file_path = 'test2.txt'
    with open(test_file_path, 'w') as f:
        f.write('Test Content')
    
    # Act
    result = edit_file(test_file_path, 'Nonexistent', 'Replacement')
    
    # Assert
    assert result == 'error: old_str not found in file'
