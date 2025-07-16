"""
Worker classes for background tasks in Image Deduplicator.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool
from PIL import Image
import imagehash

from script.translations import t

logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, dict)  # message, duplicates
    error = pyqtSignal(str)

class ImageComparisonWorker(QRunnable):
    """Worker thread for image comparison."""
    
    def __init__(self, folder: str, recursive: bool = True, similarity_threshold: int = 85):
        super().__init__()
        self.folder = folder
        self.recursive = recursive
        self.similarity_threshold = similarity_threshold
        self.signals = WorkerSignals()
        self.is_running = True

    def run(self):
        """Main processing function that runs in a separate thread."""
        try:
            # Get all image files using recursive search
            supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', 
                                  '.tiff', '.tif', '.psd', '.webp', '.svg')
            image_files = []
            
            # Normalize folder path to ensure correct path handling
            folder = os.path.abspath(self.folder)
            
            logger.info(f"Scanning for images in: {folder}")
            
            if self.recursive:
                # Use os.walk for more reliable recursive search
                for root, _, files in os.walk(folder):
                    if not self.is_running:
                        return
                        
                    for f in files:
                        if f.lower().endswith(supported_extensions):
                            try:
                                full_path = os.path.abspath(os.path.join(root, f))
                                if os.path.isfile(full_path):
                                    image_files.append(full_path)
                            except Exception as e:
                                logger.warning(f"Error accessing file {f}: {e}")
                                continue
            else:
                # Get files from current directory only
                try:
                    for f in os.listdir(folder):
                        if not self.is_running:
                            return
                            
                        if f.lower().endswith(supported_extensions):
                            try:
                                full_path = os.path.abspath(os.path.join(folder, f))
                                if os.path.isfile(full_path):
                                    image_files.append(full_path)
                            except Exception as e:
                                logger.warning(f"Error accessing file {f}: {e}")
                                continue
                except OSError as e:
                    self.signals.error.emit(str(e))
                    return
            
            if not image_files:
                self.signals.error.emit(t('no_images_found', 'en'))
                return
            
            total_images = len(image_files)
            logger.info(f"Found {total_images} images to process")
            
            # Process images in chunks to keep UI responsive
            chunk_size = 10  # Process 10 images at a time
            hashes = {}
            
            for i in range(0, total_images, chunk_size):
                if not self.is_running:
                    return
                    
                chunk = image_files[i:i + chunk_size]
                for image_path in chunk:
                    if not self.is_running:
                        return
                        
                    try:
                        with Image.open(image_path) as img:
                            # Convert to RGB if image has an alpha channel
                            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                                img = img.convert('RGB')
                            
                            # Calculate perceptual hash
                            phash = str(imagehash.phash(img))
                            
                            if phash in hashes:
                                hashes[phash].append(image_path)
                            else:
                                hashes[phash] = [image_path]
                        
                    except Exception as e:
                        logger.warning(f"Error processing {image_path}: {e}")
                        continue
                
                # Update progress after each chunk
                progress = min(99, int((i + len(chunk)) / total_images * 100))  # Cap at 99% until done
                self.signals.progress.emit(progress)
            
            # Group duplicates
            duplicates = {}
            for file_paths in hashes.values():
                if len(file_paths) > 1:  # Only consider groups with duplicates
                    # Sort by path length (shorter paths first) to have a consistent original
                    sorted_paths = sorted(file_paths, key=len)
                    original = sorted_paths[0]
                    duplicates[original] = sorted_paths[1:]  # All others are duplicates
            
            if not duplicates:
                self.signals.finished.emit(t('no_duplicates_found', 'en'), {})
            else:
                self.signals.finished.emit(
                    t('duplicates_found', 'en', count=sum(len(dups) for dups in duplicates.values())),
                    duplicates
                )
                
        except Exception as e:
            error_msg = f"Error in image comparison: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            self.signals.error.emit(error_msg)
        finally:
            # Ensure we always signal completion
            self.signals.progress.emit(100)

    def stop(self):
        """Stop the worker thread."""
        self.is_running = False
