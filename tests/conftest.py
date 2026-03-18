import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "capability(dim): capability dimension for scoring")
