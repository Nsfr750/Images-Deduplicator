"""
Worker classes for background tasks in Image Deduplicator.
"""
import os
import concurrent.futures
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
from datetime import datetime, timedelta
import tempfile
import io

from wand.image import Image as WandImage
import imagehash
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

# Import logger from our centralized module
from script.logger import logger

# Constants
CACHE_FILE = Path("cache/image_hashes.json")
CACHE_EXPIRY_DAYS = 7  # Number of days to keep cache entries
MAX_WORKERS = os.cpu_count() or 4  # Number of worker threads
CHUNK_SIZE = 50  # Number of images to process in each chunk
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp', '.psd', '.gif', '.bmp'}

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(str, dict)  # message, duplicates
    error = pyqtSignal(str)  # Error message

class HashCache:
    """Handles caching of image hashes to disk for faster subsequent runs."""
    
    def __init__(self, cache_file: Path = CACHE_FILE):
        """Initialize the hash cache."""
        self.cache_file = cache_file
        self.cache_dir = cache_file.parent
        self.cache: Dict[str, Dict] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load the cache from disk."""
        try:
            if not self.cache_file.exists():
                self.cache = {}
                return
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache = data.get('hashes', {})
                
            # Clean up expired entries
            self.cleanup()
            
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load hash cache: {e}")
            self.cache = {}
    
    def save(self) -> None:
        """Save the cache to disk."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'hashes': self.cache}, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save hash cache: {e}")
    
    def get(self, file_path: str) -> Optional[dict]:
        """Get a cache entry for the given file path."""
        try:
            entry = self.cache.get(file_path)
            if not entry:
                return None
                
            # Check if the file has been modified since caching
            mtime = os.path.getmtime(file_path)
            if entry.get('mtime') != mtime:
                return None
                
            # Check if the entry is expired
            cache_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cache_time > timedelta(days=CACHE_EXPIRY_DAYS):
                return None
                
            return entry
            
        except (OSError, KeyError, ValueError) as e:
            logger.debug(f"Cache miss for {file_path}: {e}")
            return None
    
    def set(self, file_path: str, phash: str, ahash: str) -> None:
        """Set a cache entry for the given file path."""
        try:
            mtime = os.path.getmtime(file_path)
            self.cache[file_path] = {
                'phash': phash,
                'ahash': ahash,
                'mtime': mtime,
                'timestamp': datetime.now().isoformat()
            }
        except OSError as e:
            logger.warning(f"Failed to cache hash for {file_path}: {e}")
    
    def cleanup(self) -> None:
        """Remove expired cache entries."""
        expired_time = datetime.now() - timedelta(days=CACHE_EXPIRY_DAYS)
        to_remove = []
        
        for path, entry in self.cache.items():
            try:
                cache_time = datetime.fromisoformat(entry['timestamp'])
                if cache_time < expired_time:
                    to_remove.append(path)
            except (KeyError, ValueError):
                to_remove.append(path)
        
        for path in to_remove:
            self.cache.pop(path, None)
        
        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} expired cache entries")
            self.save()

class ImageMetadata:
    """Helper class to handle image metadata operations."""
    
    @staticmethod
    def get_metadata(image_path: str) -> Dict[str, Any]:
        """Extract metadata from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing the image metadata
        """
        try:
            with WandImage(filename=image_path) as img:
                metadata = {}
                
                # Get basic info
                metadata['format'] = img.format
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['resolution'] = (img.resolution[0], img.resolution[1])
                
                # Get EXIF data if available
                if hasattr(img, 'metadata') and 'exif:' in img.metadata:
                    metadata['exif'] = {}
                    for key, value in img.metadata.items():
                        if key.startswith('exif:'):
                            metadata['exif'][key[5:]] = value
                
                # Get other metadata
                for key in ['dpi', 'quality', 'progressive', 'icc-profile']:
                    if key in img.metadata:
                        metadata[key] = img.metadata[key]
                
                # Format-specific metadata
                if img.format in ['JPEG', 'JPG']:
                    metadata['jfif'] = img.metadata.get('jfif', {})
                
                return metadata
                
        except Exception as e:
            logger.warning(f"Error reading metadata from {image_path}: {e}")
            return {}
    
    @staticmethod
    def apply_metadata(image_path: str, metadata: Dict[str, Any]) -> bool:
        """Apply metadata to an image file.
        
        Args:
            image_path: Path to the image file
            metadata: Dictionary containing metadata to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not metadata:
            return True
            
        try:
            # Create a temporary file for the output
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(image_path).suffix) as temp_file:
                temp_path = temp_file.name
            
            try:
                with WandImage(filename=image_path) as img:
                    # Apply basic metadata
                    if 'resolution' in metadata:
                        img.resolution = metadata['resolution']
                    
                    # Apply EXIF data if available
                    if 'exif' in metadata and hasattr(img, 'metadata'):
                        for key, value in metadata['exif'].items():
                            img.metadata[f'exif:{key}'] = value
                    
                    # Apply other metadata
                    for key in ['dpi', 'quality', 'progressive', 'icc-profile']:
                        if key in metadata and metadata[key] is not None:
                            img.metadata[key] = str(metadata[key])
                    
                    # Save with metadata
                    img.save(filename=temp_path)
                    
                    # Replace original with the new file
                    shutil.move(temp_path, image_path)
                    logger.debug(f"Successfully applied metadata to {image_path}")
                    return True
                    
            except Exception as save_error:
                logger.error(f"Error saving image with metadata {image_path}: {save_error}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return False
                
        except Exception as e:
            logger.error(f"Error processing {image_path} in apply_metadata: {e}", exc_info=True)
            return False

class ImageComparisonWorker(QRunnable):
    """Worker thread for image comparison with optimized performance and caching."""
    
    def __init__(self, folder: str, recursive: bool = True, 
                 similarity_threshold: int = 85,
                 keep_better_quality: bool = True,
                 preserve_metadata: bool = True):
        """Initialize the image comparison worker.
        
        Args:
            folder: Path to the folder containing images
            recursive: Whether to search subdirectories
            similarity_threshold: Threshold for considering images similar (0-100)
            keep_better_quality: Whether to keep the higher quality image from duplicates
            preserve_metadata: Whether to preserve metadata when keeping the best quality image
        """
        super().__init__()
        self.folder = os.path.abspath(folder)
        self.recursive = recursive
        self.similarity_threshold = similarity_threshold
        self.keep_better_quality = keep_better_quality
        self.preserve_metadata = preserve_metadata
        self.signals = WorkerSignals()
        self.is_running = True
        self._stop_requested = False
        
        # Initialize hash cache
        self.hash_cache = HashCache()
    
    def stop(self) -> None:
        """Request the worker to stop processing."""
        self._stop_requested = True
        self.is_running = False
    
    def _get_image_files(self, folder: str) -> List[str]:
        """Get a list of image files in the specified folder."""
        image_files = []
        
        try:
            if self.recursive:
                for root, _, files in os.walk(folder):
                    if self._stop_requested:
                        return []
                        
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in SUPPORTED_IMAGE_EXTENSIONS:
                            image_files.append(os.path.abspath(os.path.join(root, f)))
            else:
                for f in os.listdir(folder):
                    if self._stop_requested:
                        return []
                        
                    ext = os.path.splitext(f)[1].lower()
                    if ext in SUPPORTED_IMAGE_EXTENSIONS:
                        image_files.append(os.path.abspath(os.path.join(folder, f)))
                        
        except OSError as e:
            logger.error(f"Error scanning directory: {e}")
            self.signals.error.emit(f"Error scanning directory: {e}")
            return []
        
        return image_files
    
    def _get_image_hashes(self, img_path: str) -> Tuple[str, str]:
        """Get the perceptual and average hashes for an image.
        
        Args:
            img_path: Path to the image file
            
        Returns:
            Tuple of (phash, ahash) as strings
        """
        # Try to get from cache first
        cache_entry = self.hash_cache.get(img_path)
        if cache_entry:
            return cache_entry['phash'], cache_entry['ahash']
        
        try:
            with WandImage(filename=img_path) as img:
                # Convert to RGB if needed (for consistent hashing)
                if img.colorspace != 'srgb':
                    img.transform_colorspace('srgb')
                
                # Convert Wand image to PIL Image in memory
                img_buffer = io.BytesIO()
                img.format = 'PNG'
                img.save(file=img_buffer)
                img_buffer.seek(0)
                
                # Create PIL Image from buffer
                from PIL import Image
                pil_img = Image.open(img_buffer)
                
                # Generate hashes
                phash = str(imagehash.phash(pil_img))
                ahash = str(imagehash.average_hash(pil_img))
                
                # Cache the results
                self.hash_cache.set(img_path, phash, ahash)
                
                return phash, ahash
                
        except Exception as e:
            logger.warning(f"Error processing {img_path}: {e}")
            # Return a dummy hash to avoid breaking the processing
            return "0" * 16, "0" * 16
    
    def _get_image_quality_score(self, img_path: str) -> Tuple[int, int]:
        """Calculate a quality score for an image.
        
        Args:
            img_path: Path to the image file
            
        Returns:
            Tuple of (resolution_score, file_size)
        """
        try:
            with WandImage(filename=img_path) as img:
                # Resolution score (width * height)
                resolution = img.width * img.height
                # File size in bytes
                file_size = os.path.getsize(img_path)
                return (resolution, file_size)
        except Exception as e:
            logger.warning(f"Error getting quality for {img_path}: {e}")
            return (0, 0)
    
    def _process_image_chunk(self, chunk: List[str]) -> Dict[str, List[str]]:
        """Process a chunk of images and return their hashes.
        
        Args:
            chunk: List of image file paths to process
            
        Returns:
            Dictionary mapping combined hashes to lists of matching file paths
        """
        chunk_hashes = {}
        
        for img_path in chunk:
            if self._stop_requested:
                return {}
                
            try:
                # Get hashes for the image
                phash, ahash = self._get_image_hashes(img_path)
                
                # Combine hashes for better accuracy
                combined_hash = f"{phash}:{ahash}"
                
                # Add to results
                if combined_hash in chunk_hashes:
                    chunk_hashes[combined_hash].append(img_path) 
                else:
                    chunk_hashes[combined_hash] = [img_path]
                    
            except Exception as e:
                logger.warning(f"Error processing {img_path}: {e}")
                continue
                
        return chunk_hashes
    
    def _process_duplicates(self, hashes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Process duplicate groups and keep the best quality image if enabled."""
        result = {}
        
        for _, file_paths in hashes.items():
            if len(file_paths) > 1:  # Only process groups with duplicates
                if self.keep_better_quality:
                    # Sort by quality (resolution first, then file size)
                    file_paths.sort(
                        key=lambda x: self._get_image_quality_score(x),
                        reverse=True
                    )
                    
                    # Preserve metadata from the best image if needed
                    if self.preserve_metadata and len(file_paths) > 1:
                        best_image = file_paths[0]
                        for duplicate in file_paths[1:]:
                            self._preserve_metadata_for_best_image(duplicate, best_image)
                
                # The first item is considered the original (best quality if enabled)
                original = file_paths[0]
                result[original] = file_paths[1:]
                
        return result
    
    def _preserve_metadata_for_best_image(self, original_path: str, best_path: str) -> bool:
        """Preserve metadata from the original image when keeping the best quality version.
        
        Args:
            original_path: Path to the original image (with metadata)
            best_path: Path to the best quality image (to receive metadata)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get metadata from original image
            metadata = ImageMetadata.get_metadata(original_path)
            if not metadata:
                return False
                
            # Apply metadata to best image
            return ImageMetadata.apply_metadata(best_path, metadata)
            
        except Exception as e:
            logger.warning(f"Error preserving metadata from {original_path} to {best_path}: {e}")
            return False
    
    def run(self) -> None:
        """Main processing function that runs in a separate thread."""
        try:
            if not os.path.isdir(self.folder):
                self.signals.error.emit(f"Directory not found: {self.folder}")
                return
            
            # Get all image files
            image_files = self._get_image_files(self.folder)
            if not image_files:
                self.signals.finished.emit("No image files found in the specified directory.", {})
                return
                
            total_files = len(image_files)
            self.signals.progress.emit(5)  # Initial progress
            
            logger.info(f"Found {total_files} image files to process")
            
            # Process images in chunks
            all_hashes = {}
            processed = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Split into chunks for better progress reporting
                chunks = [image_files[i:i + CHUNK_SIZE] 
                         for i in range(0, len(image_files), CHUNK_SIZE)]
                
                future_to_chunk = {
                    executor.submit(self._process_image_chunk, chunk): chunk 
                    for chunk in chunks
                }
                
                for future in concurrent.futures.as_completed(future_to_chunk):
                    if self._stop_requested:
                        logger.info("Processing stopped by user")
                        return
                        
                    chunk = future_to_chunk[future]
                    try:
                        chunk_result = future.result()
                        # Merge results
                        for key, value in chunk_result.items():
                            if key in all_hashes:
                                all_hashes[key].extend(value)
                            else:
                                all_hashes[key] = value
                                
                        processed += len(chunk)
                        progress = min(95, 5 + int((processed / total_files) * 90))
                        self.signals.progress.emit(progress)
                        
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
                        continue
            
            # Process duplicates
            logger.info("Processing duplicate groups...")
            duplicates = self._process_duplicates(all_hashes)
            
            # Save cache
            self.hash_cache.save()
            
            # Emit finished signal
            self.signals.progress.emit(100)
            
            if duplicates:
                msg = f"Found {len(duplicates)} groups of duplicate images."
            else:
                msg = "No duplicate images found."
                
            self.signals.finished.emit(msg, duplicates)
            
        except Exception as e:
            logger.error(f"Error in image comparison: {e}", exc_info=True)
            self.signals.error.emit(f"An error occurred: {str(e)}")
        finally:
            self.is_running = False
