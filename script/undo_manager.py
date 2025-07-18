"""
Undo manager for file operations in Image Deduplicator.
"""
from dataclasses import dataclass, field
from pathlib import Path
import shutil
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from script.logger import logger  # Import the enhanced logger

logger = logging.getLogger(__name__)

@dataclass
class FileOperation:
    """Represents a file operation that can be undone."""
    operation_type: str  # 'delete' or 'move'
    source: str
    destination: Optional[str] = None  # Only for move operations
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def undo(self) -> bool:
        """
        Undo this operation.
        Returns True if successful, False otherwise.
        """
        try:
            if self.operation_type == 'delete':
                # For delete operations, we can't directly undo send2trash
                # We'll move the file back from the trash if it's still there
                # Note: This is a best-effort approach as OS trash implementations vary
                if os.path.exists(self.source):
                    # If the file still exists in the original location, do nothing
                    return True
                    
                # Try to restore from trash if possible
                # Note: This is a simplified approach and may not work on all systems
                try:
                    # On Windows, the file might be in the Recycle Bin
                    # On macOS, it would be in ~/.Trash
                    # This is a simplified approach and may need adjustment
                    if os.name == 'nt':  # Windows
                        # On Windows, files in Recycle Bin have special paths
                        # We'll just try to restore the file if it still exists
                        if os.path.exists(self.source):
                            return True
                    
                    logger.warning("Undo of send2trash operation is not fully supported. "
                                 "Please restore the file from your system's trash manually.")
                    return False
                except Exception as e:
                    logger.error(f"Error during undo of send2trash operation: {e}")
                    return False
                
            elif self.operation_type == 'move':
                # For move operations, swap source and destination
                if not os.path.exists(self.destination):
                    logger.error(f"Destination file not found for undo: {self.destination}")
                    return False
                    
                shutil.move(self.destination, self.source)
                logger.info(f"Undo move: Moved {self.destination} back to {self.source}")
                return True
                
        except Exception as e:
            logger.error(f"Error undoing operation: {e}", exc_info=True)
            return False
            
        return False

class UndoManager:
    """Manages undo operations for file operations."""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the undo manager.
        
        Args:
            max_history: Maximum number of operations to keep in history
        """
        self.operations: List[FileOperation] = []
        self.max_history = max_history
    
    def add_operation(self, operation: FileOperation) -> None:
        """
        Add an operation to the undo stack.
        
        Args:
            operation: The operation to add
        """
        self.operations.append(operation)
        
        # Trim history if it gets too large
        if len(self.operations) > self.max_history:
            self.operations.pop(0)
    
    def can_undo(self) -> bool:
        """Return True if there are operations that can be undone."""
        return len(self.operations) > 0
    
    def get_last_operation(self) -> Optional[FileOperation]:
        """Get the last operation without removing it."""
        return self.operations[-1] if self.operations else None
    
    def undo_last_operation(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            bool: True if the operation was successfully undone, False otherwise
        """
        if not self.operations:
            return False
            
        operation = self.operations.pop()
        return operation.undo()
    
    def clear(self) -> None:
        """Clear all operations from the history."""
        self.operations.clear()
    
    def move_to_trash(self, file_path: str) -> str:
        """
        Move a file to the system trash using send2trash.
        
        Args:
            file_path: Path to the file to move to trash
            
        Returns:
            str: The original file path (for compatibility with undo)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: For other errors during trash operation
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Use send2trash to move the file to the system trash
            import send2trash
            send2trash.send2trash(file_path)
            logger.info(f"Moved file to trash: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error moving file to trash: {e}", exc_info=True)
            raise
