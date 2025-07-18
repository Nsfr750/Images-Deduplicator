"""
Module for displaying image previews in a dialog window.
"""
import os
from pathlib import Path
from typing import Union, List, Optional

from PyQt6.QtCore import Qt, QSize, QPoint, QRectF, QTimerEvent
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
        super().__init__(parent)
        self.logger = logger
        self.logger.debug("Initializing ImagePreviewDialog")
        
        # Set dialog properties
        self.setWindowTitle("Image Preview")
        self.setMinimumSize(800, 600)
        self.logger.debug(f"Window flags before: {self.windowFlags().to_bytes(4, 'little')}")
        
        # Set window flags to ensure it's visible
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.logger.debug(f"Window flags after: {self.windowFlags().to_bytes(4, 'little')}")
        
        # Initialize UI components
        self.image_paths = [str(p) for p in image_paths] if image_paths else []
        self.current_index = 0
        self.logger.debug(f"Initialized with {len(self.image_paths)} images")
        
        # Set up the UI
        self.init_ui()
        
        # Load the first image if available
        if self.image_paths:
            self.logger.debug("Loading first image")
            QApplication.processEvents()  # Ensure UI is ready
            self.load_image(self.current_index)
            
        # Set up timer to check visibility
        self.visibility_timer = self.startTimer(1000)  # Check every second
        
    def timerEvent(self, event: QTimerEvent):
        """Periodically check if the window is visible."""
        if not self.isVisible():
            self.logger.warning("Dialog is not visible! Attempting to show...")
            self.showNormal()
            self.raise_()
            self.activateWindow()
    
    def showEvent(self, event):
        """Handle the show event to ensure proper dialog positioning."""
        super().showEvent(event)
        self.logger.debug("Show event received")
        
        # Center the dialog on the screen
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.size()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.logger.debug(f"Moving dialog to: x={x}, y={y}")
        self.move(x, y)
        
        # Ensure the dialog is brought to the front
        self.logger.debug("Raising and activating dialog")
        self.raise_()
        self.activateWindow()
        
        # Force update
        self.update()
        QApplication.processEvents()
        
        # Log window state
        self.logger.debug(f"Dialog geometry: {self.geometry()}")
        self.logger.debug(f"Is visible: {self.isVisible()}")
        self.logger.debug(f"Is active window: {self.isActiveWindow()}")
        self.logger.debug(f"Is enabled: {self.isEnabled()}")
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Image display area
        self.image_view = ImagePreviewWidget()
        layout.addWidget(self.image_view)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.close_btn)
        
        layout.addLayout(nav_layout)
        self.update_navigation_buttons()
    
    def load_image(self, index: int) -> bool:
        """
        Load and display the image at the given index.
        
        Args:
            index: Index of the image to load
            
        Returns:
            bool: True if image was loaded successfully, False otherwise
        """
        if not self.image_paths or not (0 <= index < len(self.image_paths)):
            return False
            
        self.current_index = index
        image_path = self.image_paths[index]
        self.logger.debug(f"Loading image at index {index}: {image_path}")
        
        success = self.image_view.set_image(image_path)
        
        if success:
            self.setWindowTitle(f"Image Preview ({index + 1}/{len(self.image_paths)} - {os.path.basename(image_path)})")
        else:
            self.logger.error(f"Failed to load image: {image_path}")
        
        self.update_navigation_buttons()
        return success
    
    def show_previous(self):
        """Show the previous image in the list."""
        if self.current_index > 0:
            self.load_image(self.current_index - 1)
    
    def show_next(self):
        """Show the next image in the list."""
        if self.current_index < len(self.image_paths) - 1:
            self.load_image(self.current_index + 1)
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current index."""
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.image_paths) - 1)


def show_image_preview(image_paths: Union[str, Path, List[Union[str, Path]]], parent=None) -> None:
    """
    Show an image preview dialog in a way that's guaranteed to make it visible.
    
    Args:
        image_paths: Single path or list of image paths to display
        parent: Parent widget
    """
    try:
        # Get the logger
        logger.debug("show_image_preview called")
        
        # Ensure we have a list of paths
        if not image_paths:
            logger.error("No image paths provided")
            return
            
        if isinstance(image_paths, (str, Path)):
            image_paths = [str(image_paths)]
        else:
            image_paths = [str(p) for p in image_paths if p]
        
        # Filter out non-existent paths
        valid_paths = [p for p in image_paths if os.path.exists(p)]
        
        if not valid_paths:
            logger.error(f"No valid image paths found. Tried: {image_paths}")
            return
        
        logger.debug(f"Creating preview dialog for {len(valid_paths)} images")
        
        # Create the dialog
        dialog = ImagePreviewDialog(valid_paths, parent)
        
        # Make sure the dialog is shown as a top-level window
        dialog.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Show the dialog
        logger.debug("About to show dialog")
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Ensure the dialog is properly shown
        dialog.setWindowState(dialog.windowState() & ~Qt.WindowState.WindowMinimized)
        dialog.setWindowState(Qt.WindowState.WindowActive)
        
        # Process events to ensure the dialog is shown
        QApplication.processEvents()
        
        # Return the dialog in case the caller needs it
        return dialog
        
    except Exception as e:
        logger.error(f"Error in show_image_preview: {str(e)}", exc_info=True)
        if 'dialog' in locals():
            try:
                dialog.close()
                dialog.deleteLater()
            except:
                pass
        QMessageBox.critical(parent, "Error", f"Failed to show image preview: {str(e)}")
