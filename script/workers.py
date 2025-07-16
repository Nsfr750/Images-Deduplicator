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

from PIL import Image, ImageFile, ImageOps
from PIL.ExifTags import TAGS
import imagehash
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

# Import logger from our centralized module
from script.logger import logger

# Configure PIL to be more tolerant of image files
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Constants
CACHE_FILE = Path("cache/image_hashes.json")
CACHE_EXPIRY_DAYS = 7  # Number of days to keep cache entries
MAX_WORKERS = os.cpu_count() or 4  # Number of worker threads
CHUNK_SIZE = 50  # Number of images to process in each chunk
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp'}

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
            with Image.open(image_path) as img:
                metadata = {}
                
                # Get basic info
                info = img.info
                
                # Get EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {TAGS.get(tag, tag): value 
                           for tag, value in img._getexif().items() 
                           if tag in TAGS}
                    metadata['exif'] = exif
                
                # Get other metadata
                for key in ['dpi', 'quality', 'progressive', 'icc_profile', 'photoshop']:
                    if key in info:
                        metadata[key] = info[key]
                
                # Preserve format-specific metadata
                if img.format == 'JPEG':
                    metadata['jfif'] = info.get('jfif')
                    metadata['adobe'] = info.get('adobe')
                
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
        try:
            # Skip temporary files
            if os.path.splitext(image_path)[1].lower() == '.tmp':
                logger.debug(f"Skipping metadata application for temporary file: {image_path}")
                return False
                
            if not metadata:
                return True
                
            with Image.open(image_path) as img:
                # Skip unsupported image formats
                if img.format not in ['JPEG', 'PNG', 'TIFF', 'WEBP']:
                    logger.debug(f"Skipping metadata application for unsupported format: {img.format}")
                    return False
                    
                # Create a copy to avoid modifying the original
                img_copy = img.copy()
                
                # Prepare the info dictionary for saving
                save_kwargs = {}
                
                # Handle EXIF data
                if 'exif' in metadata and hasattr(img, '_getexif'):
                    # This is a simplified example - in a real app, you'd need to convert
                    # the EXIF dictionary back to binary format
                    pass
                
                # Handle other metadata
                for key in ['dpi', 'quality', 'progressive', 'icc_profile', 'jfif', 'adobe']:
                    if key in metadata and metadata[key] is not None:
                        save_kwargs[key] = metadata[key]
                
                # Save with metadata
                try:
                    img_copy.save(image_path, **save_kwargs)
                    logger.debug(f"Successfully applied metadata to {image_path}")
                    return True
                except Exception as save_error:
                    logger.error(f"Error saving image with metadata {image_path}: {save_error}")
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
            with Image.open(img_path) as img:
                # Convert to RGB if needed (for consistent hashing)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Generate hashes
                phash = str(imagehash.phash(img))
                ahash = str(imagehash.average_hash(img))
                
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
            with Image.open(img_path) as img:
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
    
    def _preserve_metadata_for_best_image(self, original_path: str, best_path: str) -> bool:
        """Preserve metadata from the original image when keeping the best quality version.
        
        Args:
            original_path: Path to the original image (with metadata)
            best_path: Path to the best quality image (to receive metadata)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.preserve_metadata:
            return True
            
        try:
            # Skip if the files are the same
            if os.path.samefile(original_path, best_path):
                return True
                
            # Get metadata from original
            metadata = ImageMetadata.get_metadata(original_path)
            if not metadata:
                return True  # No metadata to preserve
                
            # Create a temporary file for the best image
            temp_path = f"{best_path}.tmp"
            
            try:
                # Copy the best image to a temporary file
                shutil.copy2(best_path, temp_path)
                
                # Apply metadata to the temporary file
                success = ImageMetadata.apply_metadata(temp_path, metadata)
                
                if success:
                    # Replace the original best image with the one that has metadata
                    os.replace(temp_path, best_path)
                    logger.debug(f"Preserved metadata from {original_path} to {best_path}")
                    return True
                return False
                
            except Exception as e:
                logger.error(f"Error preserving metadata: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False
                
        except Exception as e:
            logger.error(f"Error in metadata preservation: {e}")
            return False
    
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
    
    @pyqtSlot()
    def run(self) -> None:
        """Main processing function that runs in a separate thread."""
        try:
            # Get all image files
            logger.info(f"Scanning for images in: {self.folder}")
            image_files = self._get_image_files(self.folder)
            
            if not image_files:
                self.signals.error.emit("No images found in the specified folder.")
                return
            
            total_images = len(image_files)
            logger.info(f"Found {total_images} images to process")
            
            if total_images == 0:
                self.signals.finished.emit("No images found to process.", {})
                return
            
            # Process images in chunks for better memory management
            hashes = {}
            processed = 0
            
            # Split image files into chunks for parallel processing
            chunks = [image_files[i:i + CHUNK_SIZE] 
                     for i in range(0, len(image_files), CHUNK_SIZE)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit all chunks for processing
                future_to_chunk = {
                    executor.submit(self._process_image_chunk, chunk): i
                    for i, chunk in enumerate(chunks)
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_chunk):
                    if self._stop_requested:
                        break
                        
                    chunk_result = future.result()
                    
                    # Merge chunk results
                    for h, paths in chunk_result.items():
                        if h in hashes:
                            hashes[h].extend(paths)
                        else:
                            hashes[h] = paths
                    
                    # Update progress
                    processed += 1
                    progress = min(int((processed / len(chunks)) * 100), 100)
                    self.signals.progress.emit(progress)
            
            if self._stop_requested:
                self.signals.error.emit("Operation cancelled by user.")
                return
            
            # Process duplicates
            logger.info("Processing duplicate groups...")
            duplicates = self._process_duplicates(hashes)
            
            # Save cache to disk
            try:
                self.hash_cache.save()
            except Exception as e:
                logger.warning(f"Failed to save hash cache: {e}")
            
            # Emit results
            if not duplicates:
                self.signals.finished.emit("No duplicates found.", {})
            else:
                total_duplicates = sum(len(dups) for dups in duplicates.values())
                self.signals.finished.emit(
                    f"Found {len(duplicates)} groups of duplicates ({total_duplicates} total).",
                    duplicates
                )
                
        except Exception as e:
            error_msg = f"Error in image comparison: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.signals.error.emit(error_msg)
        finally:
            # Ensure we always signal completion
            self.signals.progress.emit(100)
