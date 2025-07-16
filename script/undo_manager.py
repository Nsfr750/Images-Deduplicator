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
                # For delete operations, the source is the trash path
                if not os.path.exists(self.source):
                    logger.error(f"Source file not found for undo: {self.source}")
                    return False
                
                # Restore the file to its original location
                original_path = self.metadata.get('original_path')
                if not original_path:
                    logger.error("No original path in metadata for undo")
                    return False
                
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                
                # Move the file back
                shutil.move(self.source, original_path)
                logger.info(f"Undo delete: Restored {self.source} to {original_path}")
                return True
                
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
        self.trash_dir = os.path.join(os.path.expanduser('~'), '.image_dedup_trash')
        
        # Create trash directory if it doesn't exist
        os.makedirs(self.trash_dir, exist_ok=True)
    
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
        Move a file to the trash directory.
        
        Args:
            file_path: Path to the file to move to trash
            
        Returns:
            str: The new path in the trash directory
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Create a unique filename in the trash directory
        filename = os.path.basename(file_path)
        base, ext = os.path.splitext(filename)
        counter = 1
        trash_path = os.path.join(self.trash_dir, filename)
        
        # If a file with the same name exists, add a counter
        while os.path.exists(trash_path):
            trash_path = os.path.join(self.trash_dir, f"{base}_{counter}{ext}")
            counter += 1
            
        # Move the file to trash
        shutil.move(file_path, trash_path)
        return trash_path
