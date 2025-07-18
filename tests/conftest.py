"""
Configuration file for pytest.
This file is automatically discovered by pytest and used to define fixtures and hooks.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the script directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'script'))

# Set up test data directory
TEST_DATA_DIR = Path(__file__).parent / 'test_data'

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory."""
    # Create test_data directory if it doesn't exist
    TEST_DATA_DIR.mkdir(exist_ok=True)
    return TEST_DATA_DIR

@pytest.fixture(scope="session")
def create_test_images(test_data_dir):
    """Create test image files for testing."""
    # Create test image files if they don't exist
    test_image1 = test_data_dir / 'test1.jpg'
    test_image2 = test_data_dir / 'test2.jpg'
    
    # Create empty files for testing
    test_image1.touch(exist_ok=True)
    test_image2.touch(exist_ok=True)
    
    return {
        'test1': str(test_image1),
        'test2': str(test_image2)
    }

# Add any additional fixtures here that should be available to all tests

# This ensures that tests can find the test data
def pytest_configure(config):
    """Pytest configuration hook."""
    # Create test data directory if it doesn't exist
    (Path(__file__).parent / 'test_data').mkdir(exist_ok=True)
