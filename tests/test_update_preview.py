"""
Tests for the update_preview module.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap

# Add the script directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'script')))

# Create QApplication instance once for all tests
@pytest.fixture(scope="session")
def qapp():
    """Create and return a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No need to call app.exec_() for tests

from update_preview import update_preview as update_preview_handler

# Test data
TEST_IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data', 'test.jpg'))
TEST_IMAGE_PATH2 = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data', 'test2.jpg'))

class MockUI:
    """Mock UI class for testing."""
    def __init__(self):
        self.lang = 'en'
        self.logger = MagicMock()
    
    def load_image_preview(self, image_path, preview_widget, path_label):
        """Mock load_image_preview method."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File not found: {image_path}")
        
        # Create a small pixmap for testing
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.red)
        
        preview_widget.setPixmap(pixmap)
        path_label.setText(os.path.basename(image_path))
        path_label.setToolTip(image_path)

@pytest.fixture
def setup_ui(qapp):
    """Set up test environment with mock UI components."""
    # Create a mock UI
    ui = MockUI()
    
    # Create mock widgets
    duplicates_list = QListWidget()
    original_preview = QLabel()
    duplicate_preview = QLabel()
    original_path = QLabel()
    duplicate_path = QLabel()
    
    # Add some test items to the list
    item1 = QListWidgetItem("Test Item 1")
    item1.setData(Qt.ItemDataRole.UserRole, [TEST_IMAGE_PATH, TEST_IMAGE_PATH2])
    duplicates_list.addItem(item1)
    
    item2 = QListWidgetItem("Test Item 2")
    item2.setData(Qt.ItemDataRole.UserRole, ["invalid_path.jpg", "another_invalid.jpg"])
    duplicates_list.addItem(item2)
    
    # Select the first item by default
    duplicates_list.setCurrentItem(item1)
    
    return {
        'ui': ui,
        'duplicates_list': duplicates_list,
        'original_preview': original_preview,
        'duplicate_preview': duplicate_preview,
        'original_path': original_path,
        'duplicate_path': duplicate_path
    }

def test_update_preview_success(setup_ui, tmp_path):
    """Test successful preview update with valid image paths."""
    # Create test image files
    test_img1 = tmp_path / "test1.jpg"
    test_img2 = tmp_path / "test2.jpg"
    test_img1.touch()
    test_img2.touch()
    
    # Update item data with temp paths
    item = setup_ui['duplicates_list'].item(0)
    item.setData(Qt.ItemDataRole.UserRole, [str(test_img1), str(test_img2)])
    
    # Call the function
    update_preview_handler(
        ui=setup_ui['ui'],
        duplicates_list=setup_ui['duplicates_list'],
        original_preview=setup_ui['original_preview'],
        duplicate_preview=setup_ui['duplicate_preview'],
        original_path_label=setup_ui['original_path'],
        duplicate_path_label=setup_ui['duplicate_path']
    )
    
    # Verify the previews were updated
    assert setup_ui['original_preview'].pixmap() is not None
    assert setup_ui['duplicate_preview'].pixmap() is not None
    assert setup_ui['original_path'].text() == "test1.jpg"
    assert setup_ui['duplicate_path'].text() == "test2.jpg"

def test_update_preview_invalid_paths(setup_ui):
    """Test preview update with invalid image paths."""
    # Select the second item with invalid paths
    setup_ui['duplicates_list'].setCurrentRow(1)
    
    # Call the function
    update_preview_handler(
        ui=setup_ui['ui'],
        duplicates_list=setup_ui['duplicates_list'],
        original_preview=setup_ui['original_preview'],
        duplicate_preview=setup_ui['duplicate_preview'],
        original_path_label=setup_ui['original_path'],
        duplicate_path_label=setup_ui['duplicate_path']
    )
    
    # Verify error handling
    assert "Error" in setup_ui['original_path'].text() or setup_ui['original_path'].text() == ""
    assert "Error" in setup_ui['duplicate_path'].text() or setup_ui['duplicate_path'].text() == ""

def test_update_preview_no_selection(setup_ui):
    """Test behavior when no item is selected."""
    # Clear selection
    setup_ui['duplicates_list'].clearSelection()
    
    # Call the function
    update_preview_handler(
        ui=setup_ui['ui'],
        duplicates_list=setup_ui['duplicates_list'],
        original_preview=setup_ui['original_preview'],
        duplicate_preview=setup_ui['duplicate_preview'],
        original_path_label=setup_ui['original_path'],
        duplicate_path_label=setup_ui['duplicate_path']
    )
    
    # Verify previews are cleared
    assert setup_ui['original_preview'].pixmap() is None or setup_ui['original_preview'].pixmap().isNull()
    assert setup_ui['duplicate_preview'].pixmap() is None or setup_ui['duplicate_preview'].pixmap().isNull()

@patch('update_preview.logger')
def test_update_preview_exception_handling(mock_logger, setup_ui):
    """Test exception handling in update_preview."""
    # Mock an exception in the UI's load_image_preview method
    def mock_load_image_preview(*args, **kwargs):
        raise Exception("Test exception")
    
    setup_ui['ui'].load_image_preview = mock_load_image_preview
    
    # Call the function
    update_preview_handler(
        ui=setup_ui['ui'],
        duplicates_list=setup_ui['duplicates_list'],
        original_preview=setup_ui['original_preview'],
        duplicate_preview=setup_ui['duplicate_preview'],
        original_path_label=setup_ui['original_path'],
        duplicate_path_label=setup_ui['duplicate_path']
    )
    
    # Verify error was logged
    assert mock_logger.error.called
    assert "Test exception" in str(mock_logger.error.call_args)
