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
    backup_path: Optional[str] = None  # Path to backup file for delete operations

    def __post_init__(self):
        """Initialize backup path for delete operations."""
        if self.operation_type == 'delete' and not self.backup_path:
            # Create a backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(self.source), '.image_dedup_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create a unique backup filename
            filename = os.path.basename(self.source)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")

    def undo(self) -> bool:
        """
        Undo this operation.
        Returns True if successful, False otherwise.
        """
        try:
            if self.operation_type == 'delete':
                # For delete operations, we need to restore from backup
                if not self.backup_path or not os.path.exists(self.backup_path):
                    logger.error(f"Backup file not found for undo: {self.backup_path}")
                    return False
                
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(self.source), exist_ok=True)
                
                # Restore the file from backup
                shutil.copy2(self.backup_path, self.source)
                logger.info(f"Undo delete: Restored {self.source} from backup")
                
                # Clean up the backup file
                try:
                    os.remove(self.backup_path)
                    # Try to remove the backup directory if it's empty
                    backup_dir = os.path.dirname(self.backup_path)
                    if os.path.exists(backup_dir) and not os.listdir(backup_dir):
                        os.rmdir(backup_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up backup file: {e}")
                
                return True
                
            elif self.operation_type == 'move':
                # For move operations, swap source and destination
                if not os.path.exists(self.destination):
                    logger.error(f"Destination file not found for undo: {self.destination}")
                    return False
                    
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(self.source), exist_ok=True)
                
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
        Move a file to the system trash using send2trash and create a backup for undo.
        
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
            # Create a backup of the file before moving to trash
            backup_dir = os.path.join(os.path.dirname(file_path), '.image_dedup_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create a unique backup filename
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")
            
            # Create the backup
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup of {file_path} at {backup_path}")
            
            # Create the file operation with backup path
            operation = FileOperation(
                operation_type='delete',
                source=file_path,
                backup_path=backup_path
            )
            
            # Add to undo stack before performing the operation
            self.add_operation(operation)
            
            try:
                # Move the file to trash
                import send2trash
                send2trash.send2trash(file_path)
                logger.info(f"Moved file to trash: {file_path}")
                
                return file_path
                
            except Exception as e:
                # If send2trash fails, clean up the backup
                logger.error(f"Failed to move file to trash: {e}")
                if os.path.exists(backup_path):
                    try:
                        os.remove(backup_path)
                        # Remove backup directory if empty
                        if os.path.exists(backup_dir) and not os.listdir(backup_dir):
                            os.rmdir(backup_dir)
                    except Exception as cleanup_error:
                        logger.error(f"Failed to clean up backup after error: {cleanup_error}")
                raise
                
        except Exception as e:
            logger.error(f"Error in move_to_trash for {file_path}: {e}", exc_info=True)
            raise
