import os
import pytest
from src.ginji import read_file, edit_file, list_files

def test_read_file_success():
    # Arrange
    test_file_path = 'test.txt'
    with open(test_file_path, 'w') as f:
        f.write('Hello World')
    
    # Act
    result = read_file(test_file_path)
    
    # Assert
    assert result == 'Hello World'

def test_read_file_non_existing():
    # Arrange
    test_file_path = 'non_existing.txt'
    
    # Act
    result = read_file(test_file_path)
    
    # Assert
    assert result.startswith('error: unable to navigate to file at:')

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

def test_list_files_success():
    # Arrange
    os.makedirs('test_dir', exist_ok=True)
    with open('test_dir/test.txt', 'w') as f:
        f.write('File content')
    
    # Act
    result = list_files('test_dir')
    
    # Assert
    assert 'test.txt' in result
    

def test_list_files_empty_directory():
    # Arrange
    os.makedirs('empty_dir', exist_ok=True)
    
    # Act
    result = list_files('empty_dir')
    
    # Assert
    assert result == ''