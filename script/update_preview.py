"""
Module for handling image preview updates in the Image Deduplicator application.
"""
from pathlib import Path
from typing import Union, Optional, Any, Tuple, List
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
import os
import time
from script.logger import logger

def update_preview(ui, duplicates_list, original_preview, duplicate_preview, 
                  original_path_label, duplicate_path_label, lang='en') -> None:
    """
    Update the image preview based on the current selection.
    
    Args:
        ui: The main UI instance
        duplicates_list: The QListWidget containing duplicate items
        original_preview: The widget to display the original image
        duplicate_preview: The widget to display the duplicate image
        original_path_label: The label to display the original image path
        duplicate_path_label: The label to display the duplicate image path
        lang: Language code for translations (default: 'en')
    """
    try:
        logger.debug("Starting update_preview")
        
        # Safely clear previews first
        try:
            if hasattr(original_preview, 'clear'):
                original_preview.clear()
            if hasattr(duplicate_preview, 'clear'):
                duplicate_preview.clear()
            if hasattr(original_path_label, 'clear'):
                original_path_label.clear()
            if hasattr(duplicate_path_label, 'clear'):
                duplicate_path_label.clear()
        except Exception as clear_error:
            logger.error(f"Error clearing previews: {clear_error}", exc_info=True)
        
        # Safely get selected items
        try:
            if not hasattr(duplicates_list, 'selectedItems'):
                logger.error("duplicates_list has no selectedItems method")
                return
                
            selected_items = duplicates_list.selectedItems()
            logger.debug(f"Selected items count: {len(selected_items) if selected_items else 0}")
            
            if not selected_items:
                logger.debug("No items selected, previews cleared")
                return
            
            # Get the first selected item
            item = selected_items[0]
            if not item:
                logger.error("Selected item is None")
                return
                
            # Safely get item text for logging
            item_text = "[No text]"
            try:
                item_text = item.text() if hasattr(item, 'text') and callable(item.text) else "[No text method]"
            except Exception as text_error:
                logger.warning(f"Could not get item text: {text_error}")
            
            logger.debug(f"Selected item text: {item_text}")
            
            # Safely get item data
            try:
                item_data = item.data(Qt.ItemDataRole.UserRole) if hasattr(item, 'data') else None
                logger.debug(f"Item data type: {type(item_data)}")
                
                if item_data is None:
                    logger.error("No data associated with selected item")
                    if hasattr(original_path_label, 'setText'):
                        original_path_label.setText("Error: No image data")
                    return
                    
                # Convert to list/tuple if it's a single path
                if not isinstance(item_data, (list, tuple)):
                    item_data = [item_data]
                
                if len(item_data) >= 2:
                    original_path = item_data[0]
                    duplicate_path = item_data[1]
                    
                    # Validate paths
                    if not isinstance(original_path, (str, Path)) or not isinstance(duplicate_path, (str, Path)):
                        error_msg = f"Invalid path types - original: {type(original_path)}, duplicate: {type(duplicate_path)}"
                        logger.error(error_msg)
                        if hasattr(original_path_label, 'setText'):
                            original_path_label.setText("Error: Invalid path types")
                        return
                    
                    logger.debug(f"Original path: {original_path}")
                    logger.debug(f"Duplicate path: {duplicate_path}")
                    
                    # Load previews independently so one failure doesn't affect the other
                    try:
                        if hasattr(ui, 'load_image_preview') and hasattr(original_preview, 'setPixmap'):
                            ui.load_image_preview(original_path, original_preview, original_path_label)
                    except Exception as preview_error:
                        logger.error(f"Failed to load original preview: {preview_error}", exc_info=True)
                        if hasattr(original_path_label, 'setText'):
                            original_path_label.setText(f"Error: {str(preview_error)[:50]}...")
                    
                    try:
                        if hasattr(ui, 'load_image_preview') and hasattr(duplicate_preview, 'setPixmap'):
                            ui.load_image_preview(duplicate_path, duplicate_preview, duplicate_path_label)
                    except Exception as preview_error:
                        logger.error(f"Failed to load duplicate preview: {preview_error}", exc_info=True)
                        if hasattr(duplicate_path_label, 'setText'):
                            duplicate_path_label.setText(f"Error: {str(preview_error)[:50]}...")
                    
                else:
                    error_msg = f"Unexpected item data format: {type(item_data)}"
                    logger.error(error_msg)
                    if hasattr(original_path_label, 'setText'):
                        original_path_label.setText("Error: Invalid data format")
            
            except Exception as data_error:
                logger.error(f"Error processing item data: {data_error}", exc_info=True)
                if hasattr(original_path_label, 'setText'):
                    original_path_label.setText("Error: Could not load preview")
        
        except Exception as selection_error:
            logger.error(f"Error processing selection: {selection_error}", exc_info=True)
            if hasattr(original_path_label, 'setText'):
                original_path_label.setText("Error: Invalid selection")
            
    except Exception as e:
        error_msg = f"Unexpected error in update_preview: {e}"
        logger.error(error_msg, exc_info=True)
        try:
            # Last resort cleanup
            if hasattr(original_preview, 'clear'):
                original_preview.clear()
            if hasattr(duplicate_preview, 'clear'):
                duplicate_preview.clear()
            if hasattr(original_path_label, 'setText'):
                original_path_label.setText("Error: Preview failed")
            if hasattr(duplicate_path_label, 'clear'):
                duplicate_path_label.clear()
        except Exception as clear_error:
            logger.error(f"Error clearing preview after error: {clear_error}", exc_info=True)
