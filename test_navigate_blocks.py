from src.ginji import navigate_code_blocks
from pathlib import Path

def main():
    # Create in-memory tests with a temporary directory structure
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        # Creating test files
        with open(os.path.join(temp_dir, 'one.py'), 'w') as f:
            f.write('def test_one():\n    return 1\n')
        with open(os.path.join(temp_dir, 'two.py'), 'w') as f:
            f.write('def test_two():\n    return 2\n')

        # Running navigate_code_blocks on the temp directory
        result = navigate_code_blocks('test_', temp_dir)
        print("Result:", result)

        # Run no matches test
        with open(os.path.join(temp_dir, 'three.py'), 'w') as f:
            f.write('def nothing():\n    return None\n')

        result_no_matches = navigate_code_blocks('test_', temp_dir)
        print("No matches Result:", result_no_matches)

if __name__ == '__main__':
    main()