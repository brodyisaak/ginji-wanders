from src.ginji import search_files

def test_search_files():
    result = search_files('test_pattern', '.')  # Adjust the pattern as needed
    assert result is not None

if __name__ == '__main__':
    test_search_files()