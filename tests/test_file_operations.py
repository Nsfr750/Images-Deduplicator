"""
Tests for file operations including deletion and undo functionality.
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt

# Add the script directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'script'))

from undo_manager import UndoManager, FileOperation
import send2trash

# Test data
TEST_FILES_DIR = Path(__file__).parent / 'test_files'

def create_test_file(file_path):
    """Create a test file with some content."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("Test content for " + str(file_path))
    return file_path

@pytest.fixture(scope="module")
def qapp():
    """Create and return a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def temp_dir():
    """Create and return a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def test_files(temp_dir):
    """Create test files in a temporary directory."""
    files = []
    for i in range(3):
        file_path = temp_dir / f"test_file_{i}.txt"
        create_test_file(file_path)
        files.append(file_path)
    return files

@pytest.fixture
def undo_manager():
    """Create and return an UndoManager instance."""
    return UndoManager()

def test_move_to_trash_success(undo_manager, test_files, temp_dir):
    """Test moving a file to trash successfully."""
    file_path = test_files[0]
    
    # Mock send2trash to avoid actual file operations
    with patch('send2trash.send2trash') as mock_send2trash:
        # Call the method
        result = undo_manager.move_to_trash(str(file_path))
        
        # Verify the result
        assert result == str(file_path)
        
        # Verify send2trash was called with the correct path
        mock_send2trash.assert_called_once_with(str(file_path))

def test_move_to_trash_nonexistent_file(undo_manager, temp_dir):
    """Test moving a non-existent file to trash."""
    non_existent_file = temp_dir / "nonexistent.txt"
    
    with pytest.raises(FileNotFoundError):
        undo_manager.move_to_trash(str(non_existent_file))

def test_undo_operation(undo_manager, test_files, temp_dir):
    """Test undoing a file operation."""
    file_path = test_files[0]
    
    # Add an operation to the undo stack
    operation = FileOperation(
        operation_type='delete',
        source=str(file_path)
    )
    
    # Mock the undo method
    with patch.object(operation, 'undo', return_value=True) as mock_undo:
        # Add the operation to the undo manager
        undo_manager.add_operation(operation)
        
        # Undo the operation
        result = undo_manager.undo_last_operation()
        
        # Verify the result
        assert result is True
        mock_undo.assert_called_once()

def test_undo_with_no_operations(undo_manager):
    """Test undoing when there are no operations."""
    assert undo_manager.undo_last_operation() is False

def test_file_operation_undo_delete(monkeypatch, temp_dir):
    """Test undoing a delete operation with send2trash."""
    # Create a test file
    test_file = temp_dir / "test_undo_delete.txt"
    test_file.write_text("Test content")
    
    # Create a file operation for deletion
    operation = FileOperation(
        operation_type='delete',
        source=str(test_file)
    )
    
    # Mock send2trash to simulate the file was deleted
    with patch('send2trash.send2trash'):
        # Delete the file
        test_file.unlink()
        
        # Undo the operation - should return False since we can't fully undo send2trash
        with patch('shutil.move') as mock_move:
            result = operation.undo()
            
            # Verify the result is False since we can't fully undo send2trash
            assert result is False
            mock_move.assert_not_called()

def test_file_operation_undo_move(monkeypatch, temp_dir):
    """Test undoing a move operation."""
    # Create source and destination files
    src_file = temp_dir / "source.txt"
    dest_file = temp_dir / "dest.txt"
    src_file.write_text("Test content")
    
    # Create a file operation for move
    operation = FileOperation(
        operation_type='move',
        source=str(src_file),
        destination=str(dest_file)
    )
    
    # Mock the file operations
    with patch('os.path.exists', return_value=True), \
         patch('shutil.move') as mock_move:
        
        # Undo the operation - should move the file back
        result = operation.undo()
        
        # Verify the result
        assert result is True
        mock_move.assert_called_once_with(str(dest_file), str(src_file))

# Test UI integration
class MockUI:
    """Mock UI class for testing."""
    def __init__(self):
        self.lang = 'en'
        self.logger = MagicMock()
        self.undo_manager = UndoManager()

def test_ui_delete_selected(qapp, temp_dir):
    """Test the delete_selected method in the UI."""
    # Create test files - keep as Path objects for file creation
    test_files = [temp_dir / f"test_ui_{i}.txt" for i in range(2)]
    for file_path in test_files:
        create_test_file(file_path)
    
    # Create mock UI
    ui = MockUI()
    ui.duplicates_list = QListWidget()
    
    # Store the items to keep track of them
    selected_items = []
    
    # Add test items to the list with the correct data role
    # Convert to strings for the UI
    test_file_strings = [str(fp) for fp in test_files]
    for file_path in test_file_strings:
        item = QListWidgetItem()
        # Store the file path in the item's data with UserRole
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        # Also set the display text
        item.setText(file_path)
        ui.duplicates_list.addItem(item)
        selected_items.append(item)
    
    # Select all items
    for item in selected_items:
        item.setSelected(True)
    
    # Mock QMessageBox to automatically confirm deletion
    with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes), \
         patch('send2trash.send2trash') as mock_send2trash, \
         patch('os.path.exists', return_value=True), \
         patch.object(ui.duplicates_list, 'selectedItems', return_value=selected_items):
        
        # Create a real UI instance
        from UI import UI as UIClass
        ui_instance = UIClass({}, 'en')
        ui_instance.duplicates_list = ui.duplicates_list
        ui_instance.undo_manager = ui.undo_manager
        ui_instance.status_bar = MagicMock()
        ui_instance.logger = MagicMock()  # Add logger mock
        
        # Replace the actual implementation with our testable version
        def mock_update_preview():
            pass
            
        ui_instance.update_preview = mock_update_preview
        ui_instance.update_button_states = MagicMock()
        
        # Call the method
        ui_instance.delete_selected()
        
        # Verify files were sent to trash
        assert mock_send2trash.call_count == len(test_files)
        
        # Verify the correct files were sent to trash
        for file_path in test_file_strings:
            mock_send2trash.assert_any_call(file_path)
        
        # Verify undo manager has the operations
        assert len(ui_instance.undo_manager.operations) == len(test_files)
