"""
Standard library test runner for FinTech Privacy Filter.
Automatically discovers and executes all test suites under privacy_filter/tests.
"""

import sys
import unittest
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

if __name__ == "__main__":
    test_dir = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(start_dir=str(test_dir), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
