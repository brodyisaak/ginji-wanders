import pytest


def test_import_src():
    try:
        from src.ginji import bash_exec
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")