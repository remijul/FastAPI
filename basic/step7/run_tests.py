import pytest
import os
import sys

def run_tests():
    """Run the API tests"""
    # Set environment variables for testing if needed
    os.environ["TESTING"] = "1"
    
    # Run pytest
    result = pytest.main(["-v", "tests/"])
    
    return result

if __name__ == "__main__":
    sys.exit(run_tests())