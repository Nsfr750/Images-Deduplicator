"""
Worker classes for background tasks in Image Deduplicator.
"""
import os
import concurrent.futures
import errno
import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from datetime import datetime, timedelta
import tempfile
import io
import pickle
from dataclasses import dataclass, field
from enum import Enum, auto

class ProgressState(Enum):
    NOT_STARTED = auto()
    SCANNING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    PAUSED = auto()
    ERROR = auto()

@dataclass
class ProgressData:
    """Class to hold progress data for saving and resuming operations."""
    state: ProgressState = ProgressState.NOT_STARTED
    folder: str = ""
    recursive: bool = True
    processed_files: List[str] = field(default_factory=list)
    remaining_files: List[str] = field(default_factory=list)
    duplicates: Dict[str, List[str]] = field(default_factory=dict)
    current_batch: List[str] = field(default_factory=list)
    hashes: Dict[str, List[str]] = field(default_factory=dict)
    total_files: int = 0
    processed_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class ProgressManager:
    """Manages saving and loading progress for long-running operations."""
    
    def __init__(self, progress_file: Union[str, Path] = "progress.bin"):
        """Initialize the progress manager.
        
        Args:
            progress_file: Path to the file where progress will be saved
        """
        self.progress_file = Path(progress_file)
        self.progress_dir = self.progress_file.parent
        self.progress_dir.mkdir(parents=True, exist_ok=True)
    
    def save_progress(self, progress_data: ProgressData) -> bool:
        """Save the current progress to disk.
        
        Args:
            progress_data: The progress data to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Create a temporary file first to ensure atomic write
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                pickle.dump(progress_data, f)
            
            # On Windows, we need to remove the destination file first if it exists
            if self.progress_file.exists():
                self.progress_file.unlink()
                
            # Rename the temp file to the actual file
            temp_file.rename(self.progress_file)
            return True
            
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            return False
    
    def load_progress(self) -> Optional[ProgressData]:
        """Load the saved progress from disk.
        
        Returns:
            Optional[ProgressData]: The loaded progress data, or None if loading failed
        """
        try:
            if not self.progress_file.exists():
                return None
                
            with open(self.progress_file, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            return None
    
    def clear_progress(self) -> bool:
        """Clear the saved progress.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error clearing progress: {e}")
            return False

@dataclass
class ComparisonMetrics:
    """Performance metrics collected during an image comparison run."""
    total_files: int = 0
    size_filtered_files: int = 0
    hashed_files: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    inaccessible_dirs: int = 0
    scan_time_seconds: float = 0.0
    hash_time_seconds: float = 0.0
    total_time_seconds: float = 0.0

    @property
    def files_per_second(self) -> float:
        """Throughput in files per second over the hashing stage."""
        return self.hashed_files / self.hash_time_seconds if self.hash_time_seconds > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Return the metrics as a plain dictionary."""
        return {
            'total_files': self.total_files,
            'size_filtered_files': self.size_filtered_files,
            'hashed_files': self.hashed_files,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'errors': self.errors,
            'inaccessible_dirs': self.inaccessible_dirs,
            'scan_time_seconds': round(self.scan_time_seconds, 3),
            'hash_time_seconds': round(self.hash_time_seconds, 3),
            'total_time_seconds': round(self.total_time_seconds, 3),
            'files_per_second': round(self.files_per_second, 2),
        }

from wand.image import Image as WandImage
import imagehash
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

# Import logger from our centralized module
from script.logger import logger

# Constants
CACHE_FILE = Path("cache/image_hashes.json")
PROGRESS_FILE = Path("cache/scan_progress.bin")
CACHE_EXPIRY_DAYS = 7  # Number of days to keep cache entries
MAX_WORKERS = os.cpu_count() or 4  # Number of worker threads
CHUNK_SIZE = 50  # Number of images to process in each chunk
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp', '.psd', '.gif', '.bmp'}
MAX_SIMILARITY_KEYS = 2000  # Max unique hash keys for pairwise similarity clustering

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    progress = pyqtSignal(int)  # Progress percentage
    progress_details = pyqtSignal(int, int, str)  # current, total, status
    finished = pyqtSignal(str, dict)  # message, duplicates
    error = pyqtSignal(str)  # Error message
    paused = pyqtSignal()  # Emitted when processing is paused
    resumed = pyqtSignal()  # Emitted when processing is resumed
    progress_saved = pyqtSignal(str)  # Path to saved progress file
    progress_loaded = pyqtSignal(bool)  # Whether progress was successfully loaded
    state_changed = pyqtSignal(str)  # Current state as string
    metrics_ready = pyqtSignal(dict)  # Performance metrics of the finished run

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
                if hasattr(img, 'metadata') and any(
                        key.startswith('exif:') for key in img.metadata):
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
                 preserve_metadata: bool = True,
                 batch_size: int = 50,
                 use_file_size: bool = True,
                 progress_file: Optional[Union[str, Path]] = None):
        """Initialize the image comparison worker.

        Args:
            folder: Path to the folder containing images
            recursive: Whether to search subdirectories
            similarity_threshold: Threshold for considering images similar (0-100)
            keep_better_quality: Whether to keep the higher quality image from duplicates
            preserve_metadata: Whether to preserve metadata when keeping the best quality image
            batch_size: Number of images to process in each batch (default: 50)
            use_file_size: Use file size comparison as an additional duplicate
                detection method — pre-filters candidates by file size and only
                reports same-size groups as duplicates (default: True)
            progress_file: Path to the file where scan progress is saved for
                resuming interrupted operations (default: cache/scan_progress.bin)
        """
        super().__init__()
        self.folder = os.path.abspath(folder)
        self.recursive = recursive
        self.similarity_threshold = similarity_threshold
        self.keep_better_quality = keep_better_quality
        self.preserve_metadata = preserve_metadata
        self.batch_size = max(1, min(batch_size, 200))  # Ensure batch size is between 1 and 200
        self.use_file_size = use_file_size
        self.signals = WorkerSignals()
        self.is_running = True
        self._stop_requested = False

        # Initialize hash cache, progress manager and metrics
        self.hash_cache = HashCache()
        self.progress_manager = ProgressManager(progress_file or PROGRESS_FILE)
        self.metrics = ComparisonMetrics()
        self._scan_started_at = datetime.now()

        # File size cache — avoids repeated stat calls during grouping/scoring
        self._file_sizes: Dict[str, int] = {}

        # Quality score of the leading image of each duplicate group
        self.quality_scores: Dict[str, Tuple[int, int, int]] = {}

        # Track processed files and batches
        self._processed_count = 0
        self._total_files = 0
    
    def stop(self) -> None:
        """Request the worker to stop processing."""
        self._stop_requested = True
        self.is_running = False
    
    def _describe_fs_error(self, err: OSError, path: Optional[str] = None) -> str:
        """Map filesystem errors to user-friendly messages.

        Covers common cases for network drives (UNC paths), permission
        problems and missing folders.

        Args:
            err: The caught OSError
            path: The path the error relates to (defaults to the scan folder)

        Returns:
            A human-readable error description
        """
        target = path or getattr(err, 'filename', None) or self.folder
        winerror = getattr(err, 'winerror', None)
        if isinstance(err, PermissionError) or err.errno in (errno.EACCES, errno.EPERM):
            return f"Access denied: {target}. Check folder permissions."
        if winerror in (53, 67, 1231) or err.errno in (
            errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ENETDOWN,
        ):
            return f"Network drive is not accessible: {target}. Check the connection and try again."
        if isinstance(err, FileNotFoundError) or err.errno == errno.ENOENT:
            return f"Folder not found: {target}"
        return str(err)

    def _check_folder_access(self) -> Optional[str]:
        """Verify the scan folder is accessible.

        Probes the directory without listing it fully — catches offline
        network drives, permission problems and special folders early.

        Returns:
            A user-friendly error message, or None if the folder is accessible
        """
        try:
            with os.scandir(self.folder) as it:
                next(it, None)
            return None
        except OSError as e:
            return self._describe_fs_error(e)

    def _get_image_files(self, folder: str) -> List[str]:
        """Get a list of image files in the specified folder."""
        image_files = []

        try:
            if self.recursive:
                for root, _, files in os.walk(folder, onerror=self._on_walk_error):
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
            description = self._describe_fs_error(e, folder)
            logger.error(f"Error scanning directory: {description} ({e})")
            self.signals.error.emit(description)
            return []

        return image_files

    def _on_walk_error(self, err: OSError) -> None:
        """Collect errors for directories that cannot be walked into."""
        self.metrics.inaccessible_dirs += 1
        logger.warning(f"Skipping inaccessible directory: {self._describe_fs_error(err)} ({err})")
        
    def _get_file_size(self, file_path: str) -> Optional[int]:
        """Get a file's size in bytes, with caching to avoid repeated stat calls."""
        size = self._file_sizes.get(file_path)
        if size is None:
            try:
                size = os.path.getsize(file_path)
                self._file_sizes[file_path] = size
            except OSError:
                return None
        return size

    def _group_files_by_size(self, file_paths: List[str]) -> Dict[int, List[str]]:
        """Group files by their size in bytes.

        Args:
            file_paths: List of file paths to group

        Returns:
            Dictionary mapping file sizes to lists of file paths with that size
        """
        size_groups = {}
        for file_path in file_paths:
            size = self._get_file_size(file_path)
            if size is None:
                logger.warning(f"Could not get size for {file_path}")
                continue
            if size in size_groups:
                size_groups[size].append(file_path)
            else:
                size_groups[size] = [file_path]
        return size_groups
    
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
            self.metrics.cache_hits += 1
            return cache_entry['phash'], cache_entry['ahash']

        self.metrics.cache_misses += 1
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
            self.metrics.errors += 1
            logger.warning(f"Error processing {img_path}: {e}")
            # Return a dummy hash to avoid breaking the processing
            return "0" * 16, "0" * 16
    
    def _get_image_quality_score(self, img_path: str) -> Tuple[int, int, int]:
        """Calculate a composite quality score for an image.

        The score is a tuple of (pixel count, ImageMagick quality estimate,
        file size in bytes) — compared lexicographically, so resolution
        dominates, then the encoder quality (e.g. JPEG quality 0-100), then
        file size.

        Args:
            img_path: Path to the image file

        Returns:
            Tuple of (resolution, quality, file_size); (0, 0, 0) on errors
        """
        try:
            with WandImage(filename=img_path) as img:
                # Resolution score (width * height)
                resolution = img.width * img.height
                # Encoder quality estimate (JPEG quality, 0 for other formats)
                im_quality = getattr(img, 'quality', None) or 0
                # File size in bytes (from the cached stat)
                file_size = self._get_file_size(img_path) or 0
                return (resolution, int(im_quality), file_size)
        except Exception as e:
            logger.warning(f"Error getting quality for {img_path}: {e}")
            return (0, 0, 0)

    @staticmethod
    def _hex_hamming(hash_a: str, hash_b: str) -> int:
        """Hamming distance between two hex-encoded hashes in bits."""
        try:
            return (int(hash_a, 16) ^ int(hash_b, 16)).bit_count()
        except ValueError:
            # Undecodable hashes are treated as maximally different
            return max(len(hash_a), len(hash_b)) * 4 or 64

    def _hash_similarity(self, key_a: str, key_b: str) -> float:
        """Similarity percentage between two combined ``phash:ahash`` keys.

        Both components contribute equally; the result is 100 for identical
        keys and degrades with the combined Hamming distance.
        """
        phash_a, _, ahash_a = key_a.partition(':')
        phash_b, _, ahash_b = key_b.partition(':')
        distance = self._hex_hamming(phash_a, phash_b) + self._hex_hamming(ahash_a, ahash_b)
        total_bits = (max(len(phash_a), len(phash_b)) + max(len(ahash_a), len(ahash_b))) * 4
        if total_bits <= 0:
            return 0.0
        return max(0.0, (total_bits - distance) / total_bits * 100)

    def _group_by_similarity(self, hashes: Dict[str, List[str]]) -> List[List[str]]:
        """Cluster files into similarity groups.

        Combined-hash keys whose mutual similarity is at least
        ``similarity_threshold`` are merged into one group (union-find over
        pairwise comparisons). With a threshold of 100 or a single key this
        degenerates to exact-hash grouping.

        Args:
            hashes: Mapping of combined hash keys to file paths

        Returns:
            List of file-path groups containing at least two files
        """
        keys = list(hashes.keys())
        if self.similarity_threshold >= 100 or len(keys) <= 1:
            return [files for files in hashes.values() if len(files) > 1]
        if len(keys) > MAX_SIMILARITY_KEYS:
            logger.warning(
                f"Too many unique hash keys ({len(keys)}), falling back to "
                "exact-match grouping"
            )
            return [files for files in hashes.values() if len(files) > 1]

        # Union-find over the unique hash keys
        parent = {k: k for k in keys}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i, key_a in enumerate(keys):
            for key_b in keys[i + 1:]:
                if self._hash_similarity(key_a, key_b) >= self.similarity_threshold:
                    parent[find(key_b)] = find(key_a)

        clusters: Dict[str, List[str]] = {}
        for key in keys:
            clusters.setdefault(find(key), []).extend(hashes[key])
        return [files for files in clusters.values() if len(files) > 1]
    
    def _process_image_chunk(self, chunk: List[str]) -> Dict[str, List[str]]:
        """Process a chunk of images and return their hashes.
        
        Args:
            chunk: List of image file paths to process
            
        Returns:
            Dictionary mapping combined hashes to lists of matching file paths
        """
        chunk_hashes = {}
        processed = 0
        total = len(chunk)
        
        for img_path in chunk:
            if self._stop_requested:
                return {}
                
            try:
                # Update progress for this chunk
                processed += 1
                if processed % 10 == 0:  # Update progress every 10 images
                    progress = 10 + int(80 * (self._processed_count + processed) / self._total_files)
                    self.signals.progress.emit(min(progress, 90))
                
                # Get hashes for the image
                phash, ahash = self._get_image_hashes(img_path)
                self.metrics.hashed_files += 1

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
        """Process similarity groups and keep the best quality image if enabled."""
        result = {}
        self.quality_scores = {}

        for file_paths in self._group_by_similarity(hashes):
            # When file size comparison is enabled, files with matching
            # hashes are additionally validated by file size
            if self.use_file_size:
                size_groups = self._group_files_by_size(file_paths)
            else:
                size_groups = {0: file_paths}

            for size, same_size_files in size_groups.items():
                if len(same_size_files) > 1:  # Only process groups with same size
                    if self.keep_better_quality:
                        # Sort by composite quality (resolution, encoder
                        # quality, then file size)
                        same_size_files.sort(
                            key=lambda x: self._get_image_quality_score(x),
                            reverse=True
                        )

                        # Preserve metadata from the best image if needed
                        if self.preserve_metadata and len(same_size_files) > 1:
                            best_image = same_size_files[0]
                            for duplicate in same_size_files[1:]:
                                self._preserve_metadata_for_best_image(duplicate, best_image)

                    # The first item is considered the original (best quality if enabled)
                    original = same_size_files[0]
                    result[original] = same_size_files[1:]
                    self.quality_scores[original] = self._get_image_quality_score(original)

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
    
    def _iter_batches(self, file_paths: List[str]) -> List[List[str]]:
        """Split file paths into sequential batches of ``batch_size`` images.

        Args:
            file_paths: Files to split

        Returns:
            List of batches (lists of file paths)
        """
        return [
            file_paths[i:i + self.batch_size]
            for i in range(0, len(file_paths), self.batch_size)
        ]

    def _save_progress(
        self,
        state: ProgressState,
        processed_files: List[str],
        remaining_files: List[str],
        hashes: Dict[str, List[str]],
        error_message: Optional[str] = None,
    ) -> None:
        """Persist the current scan progress so the run can be resumed.

        Args:
            state: Current progress state
            processed_files: Files already hashed in this run
            remaining_files: Files still waiting to be hashed
            hashes: Combined-hash map collected so far
            error_message: Optional error description for failed runs
        """
        data = ProgressData(
            state=state,
            folder=self.folder,
            recursive=self.recursive,
            processed_files=list(processed_files),
            remaining_files=list(remaining_files),
            hashes=hashes,
            total_files=len(processed_files) + len(remaining_files),
            processed_count=len(processed_files),
            start_time=self._scan_started_at,
            end_time=datetime.now() if state in (ProgressState.COMPLETED, ProgressState.ERROR, ProgressState.PAUSED) else None,
            error_message=error_message,
        )
        if self.progress_manager.save_progress(data):
            self.signals.progress_saved.emit(str(self.progress_manager.progress_file))
            self.signals.state_changed.emit(state.name)

    def _load_saved_progress(
        self, candidate_files: List[str]
    ) -> Tuple[Dict[str, List[str]], List[str], Set[str]]:
        """Load saved progress for the same folder and split out done files.

        Args:
            candidate_files: Files selected for hashing in this run

        Returns:
            Tuple of (saved hash map, remaining files, already processed set)
        """
        empty: Tuple[Dict[str, List[str]], List[str], Set[str]] = ({}, list(candidate_files), set())
        saved = self.progress_manager.load_progress()
        if not saved:
            return empty
        if saved.folder != self.folder or saved.recursive != self.recursive:
            self.progress_manager.clear_progress()
            return empty

        processed = set(saved.processed_files)
        remaining = [f for f in candidate_files if f not in processed]
        done = processed.intersection(candidate_files)
        hashes = getattr(saved, 'hashes', None) or {}

        self.signals.progress_loaded.emit(bool(done))
        if done:
            logger.info(
                f"Resuming scan: {len(done)} files already processed, "
                f"{len(remaining)} remaining"
            )
        return hashes, remaining, done

    def _log_metrics(self) -> None:
        """Log a summary of the collected performance metrics."""
        m = self.metrics
        logger.info(
            "Comparison finished: %d files scanned, %d hashed "
            "(%d cache hits, %d misses, %d errors, %d inaccessible dirs) "
            "in %.2fs (scan %.2fs, hashing %.2fs, %.1f files/s)",
            m.total_files, m.hashed_files, m.cache_hits, m.cache_misses,
            m.errors, m.inaccessible_dirs, m.total_time_seconds,
            m.scan_time_seconds, m.hash_time_seconds, m.files_per_second,
        )

    def run(self) -> None:
        """Main processing function that runs in a separate thread."""
        run_started = time.monotonic()
        try:
            if not os.path.isdir(self.folder):
                self.signals.error.emit(f"Directory not found: {self.folder}")
                return

            # Early accessibility probe — catches offline network drives and
            # permission problems before the full scan
            access_error = self._check_folder_access()
            if access_error:
                self.signals.error.emit(access_error)
                return

            # Get all image files
            scan_started = time.monotonic()
            image_files = self._get_image_files(self.folder)
            self.metrics.scan_time_seconds = time.monotonic() - scan_started
            self.metrics.total_files = len(image_files)
            if not image_files:
                if self.metrics.inaccessible_dirs:
                    msg = (f"No image files found. {self.metrics.inaccessible_dirs} "
                           "directories were skipped (access denied).")
                else:
                    msg = "No image files found in the specified directory."
                self.signals.finished.emit(msg, {})
                return

            total_files = len(image_files)
            self.signals.progress.emit(5)  # Initial progress

            if self.use_file_size:
                # File size comparison: only files sharing a size with at
                # least one other file can be duplicates
                size_groups = self._group_files_by_size(image_files)
                potential_duplicates = [
                    f for files in size_groups.values() if len(files) > 1 for f in files
                ]
            else:
                potential_duplicates = list(image_files)

            self.metrics.size_filtered_files = len(potential_duplicates)

            if not potential_duplicates:
                self.progress_manager.clear_progress()
                self.signals.finished.emit("No potential duplicates found (based on file size).", {})
                return

            # Update progress
            self.signals.progress.emit(10)

            # Resume previously saved progress for this folder, if any
            all_hashes, remaining_files, done = self._load_saved_progress(potential_duplicates)
            processed_files: Set[str] = set(done)
            remaining_set: Set[str] = set(remaining_files)

            logger.info(
                f"Found {total_files} image files, "
                f"{len(potential_duplicates)} candidates to process "
                f"({len(remaining_files)} remaining after resume)"
            )

            self._total_files = len(potential_duplicates)
            self._processed_count = len(done)

            # Process images in sequential batches; each batch is hashed in a
            # thread pool and progress is checkpointed between batches
            hash_started = time.monotonic()
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for batch in self._iter_batches(remaining_files):
                    if self._stop_requested:
                        logger.info("Processing stopped by user")
                        self._save_progress(
                            ProgressState.PAUSED,
                            sorted(processed_files),
                            sorted(remaining_set),
                            all_hashes,
                        )
                        self.signals.paused.emit()
                        return

                    chunks = [
                        batch[i:i + CHUNK_SIZE]
                        for i in range(0, len(batch), CHUNK_SIZE)
                    ]
                    future_to_chunk = {
                        executor.submit(self._process_image_chunk, chunk): chunk
                        for chunk in chunks
                    }

                    batch_completed = True
                    for future in concurrent.futures.as_completed(future_to_chunk):
                        if self._stop_requested:
                            batch_completed = False
                            break

                        chunk = future_to_chunk[future]
                        try:
                            chunk_result = future.result()
                            for key, value in chunk_result.items():
                                if key in all_hashes:
                                    all_hashes[key].extend(value)
                                else:
                                    all_hashes[key] = value

                            processed_files.update(chunk)
                            remaining_set.difference_update(chunk)
                            self._processed_count = len(processed_files)
                            progress = min(95, 5 + int((self._processed_count / self._total_files) * 90))
                            self.signals.progress.emit(progress)

                        except Exception as e:
                            self.metrics.errors += 1
                            logger.error(f"Error processing chunk: {e}")
                            continue

                    # Checkpoint progress after every batch
                    if batch_completed:
                        self._save_progress(
                            ProgressState.PROCESSING,
                            sorted(processed_files),
                            sorted(remaining_set),
                            all_hashes,
                        )

            if self._stop_requested:
                self._save_progress(
                    ProgressState.PAUSED,
                    sorted(processed_files),
                    sorted(remaining_set),
                    all_hashes,
                )
                self.signals.paused.emit()
                return

            self.metrics.hash_time_seconds = time.monotonic() - hash_started

            # Process duplicates
            logger.info("Processing duplicate groups...")
            duplicates = self._process_duplicates(all_hashes)

            # Save cache
            self.hash_cache.save()

            # Finished — emit metrics and clear saved progress
            self.metrics.total_time_seconds = time.monotonic() - run_started
            self._log_metrics()
            self.signals.metrics_ready.emit(self.metrics.to_dict())
            self.progress_manager.clear_progress()

            # Emit finished signal
            self.signals.progress.emit(100)

            if duplicates:
                msg = f"Found {len(duplicates)} groups of duplicate images."
            else:
                msg = "No duplicate images found."
            if self.metrics.inaccessible_dirs:
                msg += (f" ({self.metrics.inaccessible_dirs} directories "
                        "were skipped — access denied)")

            self.signals.finished.emit(msg, duplicates)

        except Exception as e:
            logger.error(f"Error in image comparison: {e}", exc_info=True)
            self.signals.error.emit(f"An error occurred: {str(e)}")
        finally:
            self.is_running = False
