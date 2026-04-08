import os


def test_environment_variables():
    print(f'CURRENT_ENV: {os.environ.get("CURRENT_ENV")}')
    print('PYTHONPATH:', os.environ.get('PYTHONPATH'))
    print('PATH:', os.environ.get('PATH'))
    print('CURRENT_ENV:', os.environ.get('CURRENT_ENV'))
    assert True  # simply confirm execution