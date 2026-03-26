def test_search_case_sensitivity():
    assert search_files('test_text', '.') == expected_output
    assert search_files('Test_Text', '.', case_sensitive=False) == expected_output
    assert search_files('Test_Text', '.', case_sensitive=True) != expected_output