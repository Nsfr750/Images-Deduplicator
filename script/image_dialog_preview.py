"""
Module for displaying image previews in a dialog window.
"""
import os
from pathlib import Path
from typing import Union, List, Optional

from PyQt6.QtCore import Qt, QSize, QPoint, QRectF, QTimerEvent, QThread, QMetaObject
from PyQt6.QtGui import QPixmap, QImage, QPainter, QWheelEvent, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSizePolicy, QApplication, QFrame, QMessageBox
)
from PIL import Image, ImageQt

# Import the enhanced logger
from script.logger import logger

class ImagePreviewWidget(QGraphicsView):
    """Custom widget for displaying and interacting with image previews."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)
        
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(Qt.GlobalColor.darkGray)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        self._scale_factor = 1.0
        self._pan_start = QPoint()
        self._panning = False
        self.setMinimumSize(400, 400)
    
    def set_image(self, image_path: Union[str, Path]) -> bool:
        """
        Load and display the image from the given path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if image was loaded successfully, False otherwise
        """
        try:
            if not image_path:
                logger.error("No image path provided")
                return False
                
            path_str = str(image_path)
            if not os.path.exists(path_str):
                logger.error(f"Image path does not exist: {path_str}")
                return False
                
            # Load with Pillow for better format support
            try:
                with Image.open(path_str) as img:
                    logger.debug(f"Loaded image: {os.path.basename(path_str)}, size: {img.size}, mode: {img.mode}")
                    
                    # Convert to RGB if needed (for formats like PNG with alpha channel)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        logger.debug("Converting image with alpha channel to RGB")
                        background = Image.new('RGB', img.size, (60, 63, 65))  # Match background color
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Convert to QPixmap
                    qimg = ImageQt.ImageQt(img)
                    if qimg.isNull():
                        raise ValueError("Failed to create QImage from Pillow image")
                        
                    pixmap = QPixmap.fromImage(qimg)
                    if pixmap.isNull():
                        raise ValueError("Failed to create QPixmap from QImage")
                    
                    logger.debug(f"Created QPixmap, size: {pixmap.size().width()}x{pixmap.size().height()}")
                    
                    # Store the current scroll positions
                    h_scroll = self.horizontalScrollBar().value() if self.horizontalScrollBar() else 0
                    v_scroll = self.verticalScrollBar().value() if self.verticalScrollBar() else 0
                    
                    # Update the pixmap
                    self._pixmap_item.setPixmap(pixmap)
                    
                    # Reset the view
                    self.setSceneRect(QRectF(pixmap.rect()))
                    self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                    self._scale_factor = 1.0
                    
                    # Restore scroll positions if possible
                    if self.horizontalScrollBar():
                        self.horizontalScrollBar().setValue(h_scroll)
                    if self.verticalScrollBar():
                        self.verticalScrollBar().setValue(v_scroll)
                        
                    return True
                    
            except Exception as img_error:
                logger.error(f"Error processing image {os.path.basename(path_str)}: {str(img_error)}", exc_info=True)
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error in set_image for {image_path}: {str(e)}", exc_info=True)
            return False
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        # Zoom Factor
        zoom_factor = 1.1
        
        # Zoom In
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
            self._scale_factor *= zoom_factor
        # Zoom Out
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
            self._scale_factor /= zoom_factor
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan_start = event.pos()
            self._panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events for panning."""
        if self._panning:
            delta = event.pos() - self._pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start = event.pos()
        super().mouseMoveEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize events to maintain view."""
        if self.scene() and hasattr(self, '_pixmap_item') and self._pixmap_item and not self._pixmap_item.pixmap().isNull():
            if self._scale_factor <= 1.0:
                self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)


class ImagePreviewDialog(QDialog):
    """Dialog for displaying image previews with navigation controls."""
    
    def __init__(self, image_paths: List[Union[str, Path]] = None, parent=None):
        try:
            super().__init__(parent)
            self.logger = logger
            self.logger.debug("Initializing ImagePreviewDialog")
            
            # Initialize instance variables
            self.image_paths = []
            self.current_index = -1
            self._preview_widget = None
            self._nav_buttons = {}
            self._title_label = None
            self._path_label = None
            
            # Set dialog properties
            self.setWindowTitle("Image Preview")
            self.setMinimumSize(800, 600)
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.WindowSystemMenuHint |
                Qt.WindowType.WindowMinMaxButtonsHint |
                Qt.WindowType.WindowCloseButtonHint
            )
            
            # Set up the UI
            self.init_ui()
            
            # Load images if provided
            if image_paths:
                self.set_image_paths(image_paths)
                
            # Set up a timer to check for visibility issues
            self._visibility_timer = self.startTimer(1000)  # Check every second
            
            self.logger.debug("ImagePreviewDialog initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ImagePreviewDialog: {e}", exc_info=True)
            raise
    
    def set_image_paths(self, image_paths: List[Union[str, Path]]) -> None:
        """Set the list of image paths to display."""
        try:
            self.image_paths = [str(p) for p in image_paths if os.path.exists(str(p))]
            self.current_index = 0 if self.image_paths else -1
            
            if self.image_paths:
                self.load_image(self.current_index)
                self.update_navigation_buttons()
            else:
                self.logger.warning("No valid image paths provided")
                self.clear_preview()
                
        except Exception as e:
            self.logger.error(f"Error setting image paths: {e}", exc_info=True)
            self.clear_preview()
    
    def init_ui(self):
        """Initialize the user interface components."""
        try:
            # Main layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(5)
            
            # Title and path labels
            title_frame = QFrame()
            title_layout = QVBoxLayout(title_frame)
            title_layout.setContentsMargins(0, 0, 0, 5)
            
            self._title_label = QLabel("Image Preview")
            self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            self._path_label = QLabel()
            self._path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._path_label.setStyleSheet("color: #888; font-size: 11px;")
            self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            title_layout.addWidget(self._title_label)
            title_layout.addWidget(self._path_label)
            
            # Preview area
            self._preview_widget = ImagePreviewWidget(self)
            
            # Navigation buttons
            nav_frame = QFrame()
            nav_layout = QHBoxLayout(nav_frame)
            nav_layout.setContentsMargins(0, 5, 0, 0)
            
            self._nav_buttons = {
                'prev': QPushButton("Previous"),
                'next': QPushButton("Next"),
                'zoom_in': QPushButton("Zoom In (+)"),
                'zoom_out': QPushButton("Zoom Out (-)"),
                'fit': QPushButton("Fit to Window"),
                'close': QPushButton("Close")
            }
            
            # Connect buttons
            self._nav_buttons['prev'].clicked.connect(self.show_previous)
            self._nav_buttons['next'].clicked.connect(self.show_next)
            self._nav_buttons['zoom_in'].clicked.connect(self.zoom_in)
            self._nav_buttons['zoom_out'].clicked.connect(self.zoom_out)
            self._nav_buttons['fit'].clicked.connect(self.fit_to_window)
            self._nav_buttons['close'].clicked.connect(self.accept)
            
            # Add buttons to layout
            nav_layout.addWidget(self._nav_buttons['prev'])
            nav_layout.addWidget(self._nav_buttons['next'])
            nav_layout.addStretch()
            nav_layout.addWidget(self._nav_buttons['zoom_in'])
            nav_layout.addWidget(self._nav_buttons['zoom_out'])
            nav_layout.addWidget(self._nav_buttons['fit'])
            nav_layout.addStretch()
            nav_layout.addWidget(self._nav_buttons['close'])
            
            # Add all widgets to main layout
            layout.addWidget(title_frame)
            layout.addWidget(self._preview_widget, 1)  # Make preview area expandable
            layout.addWidget(nav_frame)
            
            # Update button states
            self.update_navigation_buttons()
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}", exc_info=True)
            raise
    
    def load_image(self, index: int) -> bool:
        """Load and display the image at the specified index."""
        try:
            if not self.image_paths or index < 0 or index >= len(self.image_paths):
                self.logger.warning(f"Invalid image index: {index}")
                self.clear_preview()
                return False
                
            image_path = self.image_paths[index]
            self.logger.debug(f"Loading image {index + 1}/{len(self.image_paths)}: {os.path.basename(image_path)}")
            
            # Update UI to show loading state
            self.setCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()
            
            # Load the image
            success = self._preview_widget.set_image(image_path)
            
            if success:
                self.current_index = index
                self.update_window_title()
                self.update_path_label()
                self.logger.debug(f"Successfully loaded image: {os.path.basename(image_path)}")
            else:
                self.logger.error(f"Failed to load image: {image_path}")
                self.clear_preview()
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error loading image: {e}", exc_info=True)
            self.clear_preview()
            return False
            
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def clear_preview(self):
        """Clear the current preview and update UI accordingly."""
        try:
            if hasattr(self, '_preview_widget') and self._preview_widget:
                self._preview_widget.clear()
            
            if hasattr(self, '_title_label') and self._title_label:
                self._title_label.setText("No Image")
                
            if hasattr(self, '_path_label') and self._path_label:
                self._path_label.clear()
                
        except Exception as e:
            self.logger.error(f"Error clearing preview: {e}", exc_info=True)
    
    def update_window_title(self):
        """Update the window title with current image info."""
        if not self.image_paths or self.current_index < 0:
            self.setWindowTitle("Image Preview")
            return
            
        try:
            filename = os.path.basename(self.image_paths[self.current_index])
            self.setWindowTitle(f"Image Preview - {filename} ({self.current_index + 1}/{len(self.image_paths)})")
        except Exception as e:
            self.logger.error(f"Error updating window title: {e}", exc_info=True)
    
    def update_path_label(self):
        """Update the path label with the current image path."""
        if not hasattr(self, '_path_label') or not self._path_label:
            return
            
        try:
            if self.image_paths and 0 <= self.current_index < len(self.image_paths):
                self._path_label.setText(self.image_paths[self.current_index])
            else:
                self._path_label.clear()
        except Exception as e:
            self.logger.error(f"Error updating path label: {e}", exc_info=True)
    
    def update_navigation_buttons(self):
        """Update the enabled state of navigation buttons."""
        if not hasattr(self, '_nav_buttons') or not self._nav_buttons:
            return
            
        try:
            has_images = bool(self.image_paths)
            has_prev = has_images and self.current_index > 0
            has_next = has_images and self.current_index < len(self.image_paths) - 1
            
            self._nav_buttons['prev'].setEnabled(has_prev)
            self._nav_buttons['next'].setEnabled(has_next)
            
            # Enable zoom/fit buttons only if we have an image
            has_current_image = has_images and 0 <= self.current_index < len(self.image_paths)
            self._nav_buttons['zoom_in'].setEnabled(has_current_image)
            self._nav_buttons['zoom_out'].setEnabled(has_current_image)
            self._nav_buttons['fit'].setEnabled(has_current_image)
            
        except Exception as e:
            self.logger.error(f"Error updating navigation buttons: {e}", exc_info=True)
    
    def show_previous(self):
        """Show the previous image in the list."""
        if self.current_index > 0:
            self.load_image(self.current_index - 1)
            self.update_navigation_buttons()
    
    def show_next(self):
        """Show the next image in the list."""
        if self.current_index < len(self.image_paths) - 1:
            self.load_image(self.current_index + 1)
            self.update_navigation_buttons()
    
    def zoom_in(self):
        """Zoom in on the current image."""
        try:
            if hasattr(self, '_preview_widget') and self._preview_widget:
                self._preview_widget.zoom_in()
        except Exception as e:
            self.logger.error(f"Error zooming in: {e}", exc_info=True)
    
    def zoom_out(self):
        """Zoom out from the current image."""
        try:
            if hasattr(self, '_preview_widget') and self._preview_widget:
                self._preview_widget.zoom_out()
        except Exception as e:
            self.logger.error(f"Error zooming out: {e}", exc_info=True)
    
    def fit_to_window(self):
        """Fit the current image to the window."""
        try:
            if hasattr(self, '_preview_widget') and self._preview_widget:
                self._preview_widget.fit_to_window()
        except Exception as e:
            self.logger.error(f"Error fitting to window: {e}", exc_info=True)
    
    def closeEvent(self, event):
        """Handle the close event to ensure proper cleanup."""
        try:
            self.logger.debug("Closing preview dialog")
            
            # Stop any active timers
            if hasattr(self, '_visibility_timer') and self._visibility_timer:
                self.killTimer(self._visibility_timer)
                
            # Clear resources
            self.clear_preview()
            
            # Clean up references
            if hasattr(self, '_preview_widget') and self._preview_widget:
                self._preview_widget.deleteLater()
                
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during dialog close: {e}", exc_info=True)
            event.accept()  # Always accept the close event


def show_image_preview(image_paths: Union[str, Path, List[Union[str, Path]]], parent=None) -> None:
    """
    Show an image preview dialog in a way that's guaranteed to make it visible.
    
    Args:
        image_paths: Single path or list of image paths to display
        parent: Parent widget
    """
    try:
        logger.debug("show_image_preview called")
        
        # Convert single path to list if needed
        if not isinstance(image_paths, (list, tuple)):
            image_paths = [image_paths]
            
        # Convert all paths to strings and filter out any invalid ones
        valid_paths = []
        for path in image_paths:
            try:
                path_str = str(path)
                if os.path.exists(path_str):
                    valid_paths.append(path_str)
                else:
                    logger.warning(f"Image path does not exist: {path_str}")
            except Exception as e:
                logger.error(f"Error processing image path {path}: {e}", exc_info=True)
        
        if not valid_paths:
            logger.error("No valid image paths provided to show_image_preview")
            if parent:
                QMessageBox.warning(
                    parent,
                    "Preview Error",
                    "No valid images to display. The files may have been moved or deleted."
                )
            return None
            
        logger.debug(f"Showing preview for {len(valid_paths)} images")
        
        # Create the dialog on the main thread
        dialog = None
        
        def create_dialog():
            nonlocal dialog
            try:
                dialog = ImagePreviewDialog(valid_paths, parent)
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
                dialog.raise_()
                dialog.activateWindow()
                logger.debug("Preview dialog shown and activated")
            except Exception as e:
                logger.error(f"Error creating preview dialog: {e}", exc_info=True)
                if parent:
                    QMessageBox.critical(
                        parent,
                        "Preview Error",
                        f"Failed to create preview dialog: {str(e)}"
                    )
        
        # Ensure we're on the main thread
        if QThread.currentThread() != QApplication.instance().thread():
            logger.debug("Scheduling dialog creation on main thread")
            QMetaObject.invokeMethod(
                QApplication.instance(),
                create_dialog,
                Qt.ConnectionType.QueuedConnection
            )
        else:
            create_dialog()
            
        return dialog
        
    except Exception as e:
        logger.error(f"Unexpected error in show_image_preview: {e}", exc_info=True)
        if parent:
            QMessageBox.critical(
                parent,
                "Preview Error",
                f"An unexpected error occurred: {str(e)}"
            )
        return None
