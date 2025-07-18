"""
Module for displaying image previews in a dialog window.
"""
import logging
import os
from pathlib import Path
from typing import Union, List, Optional

from PyQt6.QtCore import Qt, QSize, QPoint, QRectF, QTimerEvent, QThread, QMetaObject, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap, QImage, QPainter, QWheelEvent, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSizePolicy, QApplication, QFrame, QMessageBox
)
from wand.image import Image as WandImage
from wand.exceptions import WandException

# Import the enhanced logger
from script.logger import logger

class ImagePreviewWidget(QGraphicsView):
    """Custom widget for displaying and interacting with image previews."""
    
    MAX_IMAGE_DIMENSION = 4000  # Maximum width/height for images to prevent memory issues
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
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
        
        # Store the current pixmap reference to prevent garbage collection
        self._current_pixmap = None
    
    def clear(self):
        """Clear the current image and free resources."""
        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)
        self._current_pixmap = None
        self._scale_factor = 1.0
        self.resetTransform()
    
    def load_image(self, image_data: Union[QImage, QPixmap, str, Path, WandImage]):
        """
        Load an image from various sources.
        
        Args:
            image_data: Can be a QImage, QPixmap, file path (str/Path), or Wand Image
        """
        try:
            self.logger.debug(f"Loading image from source: {type(image_data).__name__}")
            
            if isinstance(image_data, (str, Path)):
                # Load from file using Wand
                file_path = str(image_data)
                self.logger.debug(f"Loading image from file: {file_path}")
                
                with WandImage(filename=file_path) as img:
                    # Convert Wand image to QPixmap
                    self._current_pixmap = self._wand_to_qpixmap(img)
            
            elif isinstance(image_data, WandImage):
                # Already a Wand image
                self._current_pixmap = self._wand_to_qpixmap(image_data)
            
            elif isinstance(image_data, QImage):
                # Convert QImage to QPixmap
                self._current_pixmap = QPixmap.fromImage(image_data)
            
            elif isinstance(image_data, QPixmap):
                # Already a QPixmap
                self._current_pixmap = image_data
            
            else:
                raise ValueError(f"Unsupported image type: {type(image_data)}")
            
            # Set the pixmap and fit to view
            if self._current_pixmap and not self._current_pixmap.isNull():
                self._pixmap_item.setPixmap(self._current_pixmap)
                self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                self._scale_factor = 1.0
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading image: {e}", exc_info=True)
            return False
    
    def _wand_to_qpixmap(self, wand_img: WandImage) -> QPixmap:
        """Convert a Wand Image to QPixmap."""
        try:
            # Convert to RGB if not already
            if wand_img.alpha_channel:
                wand_img.background_color = 'white'
                wand_img.alpha_channel = 'remove'
            
            # Convert to 8-bit RGB
            wand_img.depth = 8
            
            # Get image data as bytes
            blob = wand_img.make_blob('RGB')
            
            # Create QImage from raw data
            qimage = QImage(
                blob, 
                wand_img.width, 
                wand_img.height, 
                wand_img.width * 3,  # 3 bytes per pixel for RGB
                QImage.Format.Format_RGB888
            )
            
            # Convert to QPixmap and return
            return QPixmap.fromImage(qimage)
            
        except Exception as e:
            self.logger.error(f"Error converting Wand image to QPixmap: {e}", exc_info=True)
            return QPixmap()
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl + Wheel
            zoom_in = event.angleDelta().y() > 0
            if zoom_in:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Default behavior for scrolling
            super().wheelEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._pan_start = event.pos()
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
        if self._panning and not self._pixmap_item.pixmap().isNull():
            # Calculate the difference in mouse position
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            
            # Scroll the scrollbars by the difference
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())
            
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def zoom_in(self, factor: float = 1.25):
        """
        Zoom in on the image.
        
        Args:
            factor: The zoom factor (must be greater than 1.0)
        """
        if factor <= 1.0:
            factor = 1.25  # Default to 1.25 if invalid factor is provided
        self._scale_image(factor)
    
    def zoom_out(self, factor: float = 1.25):
        """
        Zoom out from the image.
        
        Args:
            factor: The zoom factor (must be greater than 1.0)
        """
        if factor <= 1.0:
            factor = 1.25  # Default to 1.25 if invalid factor is provided
        self._scale_image(1.0 / factor)
    
    def _scale_image(self, factor: float):
        """Scale the image by the given factor."""
        if self._pixmap_item.pixmap().isNull():
            return
        
        # Calculate new scale factor
        old_scale = self._scale_factor
        self._scale_factor *= factor
        
        # Limit zoom levels
        min_scale = 0.1
        max_scale = 10.0
        
        if self._scale_factor < min_scale:
            self._scale_factor = min_scale
            factor = min_scale / old_scale
        elif self._scale_factor > max_scale:
            self._scale_factor = max_scale
            factor = max_scale / old_scale
        
        # Apply the scale
        self.scale(factor, factor)
    
    def fit_to_view(self):
        """Fit the image to the current view."""
        if not self._pixmap_item.pixmap().isNull():
            self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            self._scale_factor = self.transform().m11()  # Update scale factor
    
    def resizeEvent(self, event):
        """Handle resize events to maintain aspect ratio."""
        super().resizeEvent(event)
        if self._pixmap_item and not self._pixmap_item.pixmap().isNull():
            self.fit_to_view()


class ImagePreviewDialog(QDialog):
    """Dialog for displaying image previews with navigation controls."""
    
    def __init__(self, image_paths: List[Union[str, Path]] = None, parent=None):
        try:
            super().__init__(parent)
            self.logger = logging.getLogger(__name__)
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
    
    def set_image_paths(self, image_paths: List[Union[str, Path]]):
        """Set the list of image paths to display."""
        try:
            self.logger.debug(f"Setting image paths: {image_paths}")
            
            # Convert all paths to strings and filter out non-existent files
            valid_paths = []
            for path in image_paths:
                path_str = str(path)
                if os.path.exists(path_str):
                    valid_paths.append(path_str)
                else:
                    self.logger.warning(f"Image file not found: {path_str}")
            
            self.image_paths = valid_paths
            self.current_index = 0 if self.image_paths else -1
            
            # Update UI based on new paths
            self.update_navigation_buttons()
            self.update_window_title()
            
            # Load the first image if available
            if self.current_index >= 0:
                self.load_image(self.current_index)
            else:
                self.clear_preview()
                
        except Exception as e:
            self.logger.error(f"Error setting image paths: {e}", exc_info=True)
    
    def init_ui(self):
        """Initialize the user interface components."""
        try:
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(5)
            
            # Title label
            self._title_label = QLabel()
            self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            main_layout.addWidget(self._title_label)
            
            # Path label
            self._path_label = QLabel()
            self._path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._path_label.setStyleSheet("color: gray; font-size: 10px;")
            self._path_label.setWordWrap(True)
            main_layout.addWidget(self._path_label)
            
            # Image preview area
            self._preview_widget = ImagePreviewWidget(self)
            main_layout.addWidget(self._preview_widget, 1)  # Stretch factor of 1
            
            # Navigation controls
            nav_layout = QHBoxLayout()
            nav_layout.setContentsMargins(0, 10, 0, 0)
            nav_layout.setSpacing(5)
            
            # Previous button
            prev_btn = QPushButton("Previous")
            prev_btn.clicked.connect(self.show_previous)
            self._nav_buttons['prev'] = prev_btn
            nav_layout.addWidget(prev_btn)
            
            # Zoom out button
            zoom_out_btn = QPushButton("Zoom Out")
            zoom_out_btn.clicked.connect(self._preview_widget.zoom_out)
            nav_layout.addWidget(zoom_out_btn)
            
            # Fit to window button
            fit_btn = QPushButton("Fit to Window")
            fit_btn.clicked.connect(self.fit_to_window)
            nav_layout.addWidget(fit_btn)
            
            # Zoom in button
            zoom_in_btn = QPushButton("Zoom In")
            zoom_in_btn.clicked.connect(self._preview_widget.zoom_in)
            nav_layout.addWidget(zoom_in_btn)
            
            # Next button
            next_btn = QPushButton("Next")
            next_btn.clicked.connect(self.show_next)
            self._nav_buttons['next'] = next_btn
            nav_layout.addWidget(next_btn)
            
            main_layout.addLayout(nav_layout)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            close_btn.setDefault(True)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            
            main_layout.addLayout(btn_layout)
            
            # Update UI state
            self.update_navigation_buttons()
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}", exc_info=True)
            raise
    
    def load_image(self, index: int):
        """Load and display the image at the specified index."""
        try:
            if not (0 <= index < len(self.image_paths)):
                self.logger.warning(f"Invalid image index: {index}")
                return False
            
            self.current_index = index
            image_path = self.image_paths[index]
            
            self.logger.debug(f"Loading image {index + 1}/{len(self.image_paths)}: {image_path}")
            
            # Update UI
            self.setCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()  # Update UI before loading
            
            # Load the image using Wand
            try:
                with WandImage(filename=image_path) as img:
                    # Update the preview widget
                    success = self._preview_widget.load_image(img)
                    
                    if success:
                        self.update_window_title()
                        self.update_path_label()
                        self.update_navigation_buttons()
                    else:
                        self.logger.error(f"Failed to load image: {image_path}")
                        QMessageBox.critical(self, "Error", f"Failed to load image: {os.path.basename(image_path)}")
                        return False
                    
                    return True
                    
            except WandException as e:
                self.logger.error(f"Wand error loading image {image_path}: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error loading image: {os.path.basename(image_path)}\n{e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading image at index {index}: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Unexpected error loading image: {e}")
            return False
            
        finally:
            self.unsetCursor()
    
    def clear_preview(self):
        """Clear the current preview and update UI accordingly."""
        self._preview_widget.clear()
        self._title_label.clear()
        self._path_label.clear()
        self.update_navigation_buttons()
    
    def update_window_title(self):
        """Update the window title with current image info."""
        if 0 <= self.current_index < len(self.image_paths):
            file_name = os.path.basename(self.image_paths[self.current_index])
            self.setWindowTitle(f"Image Preview - {file_name} ({self.current_index + 1}/{len(self.image_paths)})")
            
            # Update title label with image info
            try:
                with WandImage(filename=self.image_paths[self.current_index]) as img:
                    width, height = img.width, img.height
                    size_mb = os.path.getsize(self.image_paths[self.current_index]) / (1024 * 1024)
                    self._title_label.setText(
                        f"{file_name} • {width}×{height} • {size_mb:.2f} MB • {img.format if hasattr(img, 'format') else 'Unknown'}"
                    )
            except Exception as e:
                self.logger.warning(f"Could not get image info: {e}")
                self._title_label.setText(file_name)
    
    def update_path_label(self):
        """Update the path label with the current image path."""
        if 0 <= self.current_index < len(self.image_paths):
            self._path_label.setText(self.image_paths[self.current_index])
    
    def update_navigation_buttons(self):
        """Update the enabled state of navigation buttons."""
        has_images = len(self.image_paths) > 0
        self._nav_buttons['prev'].setEnabled(has_images and self.current_index > 0)
        self._nav_buttons['next'].setEnabled(has_images and self.current_index < len(self.image_paths) - 1)
    
    def show_previous(self):
        """Show the previous image in the list."""
        if self.current_index > 0:
            self.load_image(self.current_index - 1)
    
    def show_next(self):
        """Show the next image in the list."""
        if self.current_index < len(self.image_paths) - 1:
            self.load_image(self.current_index + 1)
    
    def zoom_in(self):
        """Zoom in on the current image."""
        self._preview_widget.zoom_in()
    
    def zoom_out(self):
        """Zoom out from the current image."""
        self._preview_widget.zoom_out()
    
    def fit_to_window(self):
        """Fit the current image to the window."""
        if hasattr(self, '_preview_widget') and self._preview_widget:
            self._preview_widget.fitInView(self._preview_widget._pixmap_item, 
                                        Qt.AspectRatioMode.KeepAspectRatio)
            self._preview_widget._scale_factor = 1.0
    
    def closeEvent(self, event):
        """Handle the close event to ensure proper cleanup."""
        try:
            if hasattr(self, '_visibility_timer') and self._visibility_timer:
                self.killTimer(self._visibility_timer)
            
            # Clear the preview to free resources
            self._preview_widget.clear()
            
            # Clear references to help with garbage collection
            self.image_paths = []
            
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during close event: {e}", exc_info=True)
            event.accept()  # Still allow the window to close
    
    def timerEvent(self, event: QTimerEvent):
        """Handle timer events for periodic checks."""
        if event.timerId() == self._visibility_timer:
            # Check if the dialog is still visible and properly initialized
            if not self.isVisible() or not self.isActiveWindow():
                return
            
            # Check if the preview widget is visible and has a valid size
            if not self._preview_widget.isVisible() or self._preview_widget.width() < 10 or self._preview_widget.height() < 10:
                self.logger.warning("Preview widget has invalid size, attempting to fix...")
                QMetaObject.invokeMethod(self, 'adjustSize', Qt.ConnectionType.QueuedConnection)
                QMetaObject.invokeMethod(self._preview_widget, 'fit_to_view', Qt.ConnectionType.QueuedConnection)
        
        super().timerEvent(event)


def show_image_preview(image_paths: Union[str, Path, List[Union[str, Path]]], parent=None):
    """
    Show an image preview dialog in a way that's guaranteed to make it visible.
    
    Args:
        image_paths: Single path or list of image paths to display
        parent: Parent widget
        
    Returns:
        Optional[ImagePreviewDialog]: The created dialog instance, or None if creation failed
    """
    try:
        logger.debug(f"show_image_preview called with paths: {image_paths}")
        
        # Convert single path to list if needed
        if not isinstance(image_paths, (list, tuple)):
            image_paths = [image_paths]
            
        # Create the dialog
        dialog = ImagePreviewDialog(image_paths, parent)
        
        # Show the dialog and wait for it to be shown
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Use a direct method call instead of invokeMethod
        QApplication.processEvents()
        dialog.fit_to_window()
        
        return dialog
        
    except Exception as e:
        logger.error(f"Error showing image preview: {e}", exc_info=True)
        return None
