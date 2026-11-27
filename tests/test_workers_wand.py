"""
Comprehensive tests for Wand-based image processing in script/workers.py.

The tests stub the heavy runtime dependencies (wand/ImageMagick, PyQt6,
imagehash, PIL) in sys.modules so the image-processing logic can be tested
without a full GUI environment. When the real dependencies are installed the
stubs are still used — the tests exercise our code, not the libraries.
"""
import os
import sys
import types
import pickle
import shutil
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Dependency stubs (must be installed into sys.modules BEFORE importing workers)
# ---------------------------------------------------------------------------

class FakeSignal:
    """Minimal stand-in for a bound pyqtSignal used in tests."""

    def __init__(self, *args, **kwargs):
        self.emissions = []

    def emit(self, *args):
        self.emissions.append(args)

    def connect(self, slot):
        pass


class SignalDescriptor:
    """Descriptor emulating pyqtSignal: one FakeSignal per instance."""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.setdefault(f'_sig_{self.name}', FakeSignal())


def _stub_modules():
    """Build stub modules for wand, imagehash, PIL and PyQt6."""
    pyqt6 = types.ModuleType('PyQt6')
    qtcore = types.ModuleType('PyQt6.QtCore')
    qtcore.QRunnable = type('QRunnable', (), {'__init__': lambda self, *a, **k: None})
    qtcore.QObject = type('QObject', (), {'__init__': lambda self, *a, **k: None})
    qtcore.pyqtSignal = lambda *a, **k: SignalDescriptor()
    qtcore.pyqtSlot = lambda *a, **k: (lambda f: f)
    pyqt6.QtCore = qtcore

    wand = types.ModuleType('wand')
    wand_image = types.ModuleType('wand.image')
    wand_image.Image = MagicMock(name='WandImage')
    wand.image = wand_image

    imagehash = types.ModuleType('imagehash')
    imagehash.phash = lambda img: 'phash_stub'
    imagehash.average_hash = lambda img: 'ahash_stub'

    pil = types.ModuleType('PIL')
    pil_image = types.ModuleType('PIL.Image')
    pil_image.open = lambda buf: buf.read()
    pil.Image = pil_image

    return {
        'PyQt6': pyqt6, 'PyQt6.QtCore': qtcore,
        'wand': wand, 'wand.image': wand_image,
        'imagehash': imagehash,
        'PIL': pil, 'PIL.Image': pil_image,
    }


def _import_workers():
    """Import script/workers.py under dependency stubs.

    Stubs are installed only for the duration of the import and removed
    afterwards, so other test modules still see the real packages.
    """
    absent = object()
    stubs = _stub_modules()
    originals = {name: sys.modules.get(name, absent) for name in stubs}
    sys.modules.update(stubs)
    sys.modules.pop('workers', None)
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'script'))
        import workers as workers_module
    finally:
        for name, original in originals.items():
            if original is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
    return workers_module


workers = _import_workers()

_STUB_MODULES = _stub_modules()


@pytest.fixture(autouse=True)
def dep_stubs():
    """Make stub modules importable during a test when real deps are missing.

    The real packages win whenever installed — the stubs only fill gaps
    (e.g. the lazy ``from PIL import Image`` inside ``_get_image_hashes``).
    """
    patched = []
    for name, module in _STUB_MODULES.items():
        try:
            __import__(name)
        except ImportError:
            patched.append(name)
            sys.modules[name] = module
    yield
    for name in patched:
        sys.modules.pop(name, None)


def _pil_open_stub():
    """Patch PIL.Image.open for pipeline tests (works with stub or real PIL)."""
    return patch.object(sys.modules['PIL'].Image, 'open', return_value=b'png-data')


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

class FakeWandImage:
    """Configurable stand-in for wand.image.Image."""

    def __init__(self, filename=None, *, width=10, height=10, format='JPEG',
                 colorspace='srgb', metadata=None, fail=None):
        self.filename = filename
        self.width = width
        self.height = height
        self.format = format
        self.colorspace = colorspace
        self.metadata = metadata or {}
        self.resolution = (72, 72)
        self._fail = fail
        if fail:
            raise fail

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def transform_colorspace(self, colorspace):
        self.colorspace = colorspace

    def save(self, file=None, filename=None):
        if file is not None:
            file.write(str(self.filename).encode())
        elif filename is not None:
            Path(filename).write_bytes(str(self.filename).encode())

    def make_blob(self):
        return str(self.filename).encode()


@pytest.fixture
def temp_dir():
    """Create and return a temporary directory for testing."""
    directory = Path(tempfile.mkdtemp())
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture
def image_files(temp_dir):
    """Create test image files with controlled sizes.

    a/b share a size, c is unique, d/e share a size.
    """
    files = {}
    for name, size in [('a.jpg', 100), ('b.jpg', 100), ('c.jpg', 50),
                       ('d.jpg', 80), ('e.jpg', 80)]:
        path = temp_dir / name
        path.write_bytes(b'x' * size)
        files[name] = str(path)
    return files


@pytest.fixture
def worker(temp_dir):
    """Create a worker instance for the temp folder."""
    w = workers.ImageComparisonWorker(
        folder=str(temp_dir),
        keep_better_quality=False,
        preserve_metadata=False,
        progress_file=temp_dir / 'progress.bin',
    )
    return w


def _last_emission(signal):
    """Return args of the last emission or None."""
    return signal.emissions[-1] if signal.emissions else None


# ---------------------------------------------------------------------------
# HashCache
# ---------------------------------------------------------------------------

class TestHashCache:
    """Tests for the on-disk image hash cache."""

    def test_set_and_get(self, temp_dir):
        target = temp_dir / 'img.jpg'
        target.write_bytes(b'x' * 10)
        cache = workers.HashCache(temp_dir / 'cache.json')
        cache.set(str(target), 'ph', 'ah')
        entry = cache.get(str(target))
        assert entry['phash'] == 'ph'
        assert entry['ahash'] == 'ah'

    def test_miss_on_changed_mtime(self, temp_dir):
        target = temp_dir / 'img.jpg'
        target.write_bytes(b'x' * 10)
        cache = workers.HashCache(temp_dir / 'cache.json')
        cache.set(str(target), 'ph', 'ah')
        # Simulate file modified after caching
        cache.cache[str(target)]['mtime'] = 0
        assert cache.get(str(target)) is None

    def test_expired_entry_is_ignored(self, temp_dir):
        target = temp_dir / 'img.jpg'
        target.write_bytes(b'x' * 10)
        cache = workers.HashCache(temp_dir / 'cache.json')
        cache.set(str(target), 'ph', 'ah')
        old = (datetime.now() - timedelta(days=workers.CACHE_EXPIRY_DAYS + 1)).isoformat()
        cache.cache[str(target)]['timestamp'] = old
        assert cache.get(str(target)) is None

    def test_persistence_round_trip(self, temp_dir):
        target = temp_dir / 'img.jpg'
        target.write_bytes(b'x' * 10)
        cache = workers.HashCache(temp_dir / 'cache.json')
        cache.set(str(target), 'ph', 'ah')
        cache.save()
        cache2 = workers.HashCache(temp_dir / 'cache.json')
        assert cache2.get(str(target))['phash'] == 'ph'

    def test_cleanup_removes_expired(self, temp_dir):
        cache = workers.HashCache(temp_dir / 'cache.json')
        old = (datetime.now() - timedelta(days=workers.CACHE_EXPIRY_DAYS + 1)).isoformat()
        cache.cache['old.jpg'] = {'phash': 'p', 'ahash': 'a', 'mtime': 0, 'timestamp': old}
        cache.cache['new.jpg'] = {'phash': 'p', 'ahash': 'a', 'mtime': 0,
                                  'timestamp': datetime.now().isoformat()}
        cache.cleanup()
        assert 'old.jpg' not in cache.cache
        assert 'new.jpg' in cache.cache


# ---------------------------------------------------------------------------
# ProgressManager / ProgressData
# ---------------------------------------------------------------------------

class TestProgressManager:
    """Tests for saving and resuming scan progress."""

    def test_save_load_round_trip(self, temp_dir):
        manager = workers.ProgressManager(temp_dir / 'prog.bin')
        data = workers.ProgressData(
            state=workers.ProgressState.PAUSED,
            folder='/scan/dir',
            recursive=True,
            processed_files=['a.jpg'],
            remaining_files=['b.jpg', 'c.jpg'],
            hashes={'h1': ['a.jpg']},
            total_files=3,
            processed_count=1,
        )
        assert manager.save_progress(data) is True
        loaded = manager.load_progress()
        assert loaded.state == workers.ProgressState.PAUSED
        assert loaded.processed_files == ['a.jpg']
        assert loaded.hashes == {'h1': ['a.jpg']}

    def test_load_missing_file(self, temp_dir):
        manager = workers.ProgressManager(temp_dir / 'missing.bin')
        assert manager.load_progress() is None

    def test_load_corrupt_file(self, temp_dir):
        path = temp_dir / 'corrupt.bin'
        path.write_bytes(b'not a pickle')
        manager = workers.ProgressManager(path)
        assert manager.load_progress() is None

    def test_clear_progress(self, temp_dir):
        path = temp_dir / 'prog.bin'
        path.write_bytes(b'x')
        manager = workers.ProgressManager(path)
        assert manager.clear_progress() is True
        assert not path.exists()


# ---------------------------------------------------------------------------
# ComparisonMetrics
# ---------------------------------------------------------------------------

class TestComparisonMetrics:
    """Tests for the performance metrics container."""

    def test_files_per_second(self):
        m = workers.ComparisonMetrics(hashed_files=100, hash_time_seconds=4.0)
        assert m.files_per_second == 25.0

    def test_files_per_second_zero_time(self):
        assert workers.ComparisonMetrics(hashed_files=10).files_per_second == 0.0

    def test_to_dict(self):
        m = workers.ComparisonMetrics(
            total_files=10, hashed_files=8, cache_hits=3, cache_misses=5,
            errors=1, scan_time_seconds=0.5, hash_time_seconds=2.0,
            total_time_seconds=3.0,
        )
        d = m.to_dict()
        assert d['total_files'] == 10
        assert d['files_per_second'] == 4.0
        assert d['errors'] == 1


# ---------------------------------------------------------------------------
# ImageMetadata (Wand metadata extraction / application)
# ---------------------------------------------------------------------------

class TestImageMetadata:
    """Tests for Wand-based metadata helpers."""

    def test_get_metadata_basic(self):
        fake = FakeWandImage(
            width=800, height=600, format='JPEG',
            metadata={'exif:Make': 'Canon', 'exif:Model': 'X100', 'dpi': '300'},
        )
        with patch.object(workers, 'WandImage', return_value=fake):
            metadata = workers.ImageMetadata.get_metadata('photo.jpg')
        assert metadata['format'] == 'JPEG'
        assert metadata['width'] == 800
        assert metadata['height'] == 600
        assert metadata['exif']['Make'] == 'Canon'
        assert metadata['dpi'] == '300'

    def test_get_metadata_error_returns_empty(self):
        with patch.object(workers, 'WandImage', side_effect=RuntimeError('boom')):
            assert workers.ImageMetadata.get_metadata('broken.jpg') == {}

    def test_apply_metadata_empty_is_noop(self):
        assert workers.ImageMetadata.apply_metadata('x.jpg', {}) is True

    def test_apply_metadata_failure(self):
        with patch.object(workers, 'WandImage', side_effect=RuntimeError('boom')):
            assert workers.ImageMetadata.apply_metadata('x.jpg', {'dpi': '300'}) is False


# ---------------------------------------------------------------------------
# Hashing pipeline (_get_image_hashes)
# ---------------------------------------------------------------------------

class TestGetImageHashes:
    """Tests for the Wand -> PNG buffer -> PIL -> imagehash pipeline."""

    def test_hashes_from_wand_image(self, worker):
        fake = FakeWandImage(colorspace='cmyk')
        with patch.object(workers, 'WandImage', return_value=fake), \
             _pil_open_stub(), \
             patch.object(workers.imagehash, 'phash', return_value='P'), \
             patch.object(workers.imagehash, 'average_hash', return_value='A'):
            phash, ahash = worker._get_image_hashes('img.jpg')
        assert (phash, ahash) == ('P', 'A')
        # Non-srgb images are normalized before hashing
        assert fake.colorspace == 'srgb'

    def test_cache_hit_skips_wand(self, worker, image_files):
        worker.hash_cache.set(image_files['a.jpg'], 'CP', 'CA')
        hits_before = worker.metrics.cache_hits
        with patch.object(workers, 'WandImage', side_effect=AssertionError('no wand')):
            phash, ahash = worker._get_image_hashes(image_files['a.jpg'])
        assert (phash, ahash) == ('CP', 'CA')
        assert worker.metrics.cache_hits == hits_before + 1

    def test_cache_miss_counted(self, worker):
        with patch.object(workers, 'WandImage', side_effect=RuntimeError('boom')):
            worker._get_image_hashes('missing.jpg')
        assert worker.metrics.cache_misses == 1
        assert worker.metrics.errors == 1

    def test_error_returns_dummy_hash(self, worker):
        with patch.object(workers, 'WandImage', side_effect=RuntimeError('boom')):
            phash, ahash = worker._get_image_hashes('broken.jpg')
        assert phash == '0' * 16
        assert ahash == '0' * 16


# ---------------------------------------------------------------------------
# Size grouping & quality scoring
# ---------------------------------------------------------------------------

class TestFileSizeComparison:
    """Tests for file size comparison detection method."""

    def test_group_by_size(self, worker, image_files):
        groups = worker._group_files_by_size(list(image_files.values()))
        assert sorted(len(v) for v in groups.values()) == [1, 2, 2]

    def test_group_by_size_unreadable(self, worker, image_files):
        groups = worker._group_files_by_size(
            list(image_files.values()) + ['/does/not/exist.jpg'])
        assert '/does/not/exist.jpg' not in sum(groups.values(), [])

    def test_same_hash_same_size_is_duplicate(self, worker, image_files):
        dups = worker._process_duplicates(
            {'h': [image_files['a.jpg'], image_files['b.jpg']]})
        assert len(dups) == 1

    def test_same_hash_different_size_dropped(self, worker, image_files):
        dups = worker._process_duplicates(
            {'h': [image_files['a.jpg'], image_files['d.jpg']]})
        assert dups == {}

    def test_same_hash_different_size_kept_without_size_check(
            self, worker, image_files):
        worker.use_file_size = False
        dups = worker._process_duplicates(
            {'h': [image_files['a.jpg'], image_files['d.jpg']]})
        assert len(dups) == 1

    def test_quality_score_from_wand(self, worker, image_files):
        fake = FakeWandImage(width=100, height=50)
        with patch.object(workers, 'WandImage', return_value=fake):
            resolution, size = worker._get_image_quality_score(image_files['a.jpg'])
        assert resolution == 5000
        assert size == 100

    def test_quality_score_error(self, worker):
        with patch.object(workers, 'WandImage', side_effect=RuntimeError('boom')):
            assert worker._get_image_quality_score('x.jpg') == (0, 0)

    def test_best_quality_sorting(self, temp_dir, image_files):
        """With keep_better_quality, the best image leads the group."""
        w = workers.ImageComparisonWorker(
            folder=str(temp_dir), keep_better_quality=True,
            preserve_metadata=False, progress_file=temp_dir / 'p.bin')
        scores = {image_files['a.jpg']: (100, 10), image_files['b.jpg']: (50, 10)}
        with patch.object(w, '_get_image_quality_score',
                          side_effect=lambda p: scores[p]):
            dups = w._process_duplicates(
                {'h': [image_files['a.jpg'], image_files['b.jpg']]})
        assert list(dups.keys()) == [image_files['a.jpg']]
        assert dups[image_files['a.jpg']] == [image_files['b.jpg']]


# ---------------------------------------------------------------------------
# Chunk processing & batching
# ---------------------------------------------------------------------------

class TestBatchProcessing:
    """Tests for chunked/batched image processing."""

    def test_iter_batches(self, worker):
        worker.batch_size = 2
        batches = worker._iter_batches(['a', 'b', 'c', 'd', 'e'])
        assert [len(b) for b in batches] == [2, 2, 1]

    def test_batch_size_clamped(self, temp_dir):
        w = workers.ImageComparisonWorker(
            folder=str(temp_dir), batch_size=500, progress_file=temp_dir / 'p.bin')
        assert w.batch_size == 200
        w = workers.ImageComparisonWorker(
            folder=str(temp_dir), batch_size=0, progress_file=temp_dir / 'p.bin')
        assert w.batch_size == 1

    def test_process_image_chunk_groups_by_hash(self, worker, image_files):
        with patch.object(worker, '_get_image_hashes',
                          side_effect=lambda p: ('H', 'H')):
            result = worker._process_image_chunk(
                [image_files['a.jpg'], image_files['b.jpg'], image_files['c.jpg']])
        assert result == {'H:H': list(sorted(
            [image_files['a.jpg'], image_files['b.jpg'], image_files['c.jpg']]))}
        assert worker.metrics.hashed_files == 3

    def test_process_image_chunk_distinct_hashes(self, worker, image_files):
        hashes = {image_files['a.jpg']: ('P1', 'A1'), image_files['b.jpg']: ('P2', 'A2')}
        with patch.object(worker, '_get_image_hashes',
                          side_effect=lambda p: hashes[p]):
            result = worker._process_image_chunk(
                [image_files['a.jpg'], image_files['b.jpg']])
        assert result == {'P1:A1': [image_files['a.jpg']],
                          'P2:A2': [image_files['b.jpg']]}


# ---------------------------------------------------------------------------
# Progress saving / resuming inside the worker
# ---------------------------------------------------------------------------

class TestProgressResume:
    """Tests for progress saving and resuming in the worker."""

    def test_save_progress_writes_file(self, worker):
        worker._save_progress(
            workers.ProgressState.PROCESSING, ['a.jpg'], ['b.jpg'], {'h': ['a.jpg']})
        assert worker.progress_manager.progress_file.exists()
        loaded = worker.progress_manager.load_progress()
        assert loaded.state == workers.ProgressState.PROCESSING
        assert loaded.processed_files == ['a.jpg']
        assert loaded.hashes == {'h': ['a.jpg']}
        assert _last_emission(worker.signals.progress_saved) is not None
        assert _last_emission(worker.signals.state_changed) == ('PROCESSING',)

    def test_load_saved_progress_skips_done(self, worker, image_files):
        manager = workers.ProgressManager(worker.progress_manager.progress_file)
        manager.save_progress(workers.ProgressData(
            state=workers.ProgressState.PAUSED,
            folder=worker.folder,
            recursive=worker.recursive,
            processed_files=[image_files['a.jpg']],
            remaining_files=[image_files['b.jpg']],
            hashes={'h': [image_files['a.jpg']]},
        ))
        hashes, remaining, done = worker._load_saved_progress(
            [image_files['a.jpg'], image_files['b.jpg']])
        assert remaining == [image_files['b.jpg']]
        assert done == {image_files['a.jpg']}
        assert hashes == {'h': [image_files['a.jpg']]}
        assert _last_emission(worker.signals.progress_loaded) == (True,)

    def test_load_saved_progress_folder_mismatch(self, worker, image_files):
        manager = workers.ProgressManager(worker.progress_manager.progress_file)
        manager.save_progress(workers.ProgressData(
            state=workers.ProgressState.PAUSED, folder='/other/dir'))
        hashes, remaining, done = worker._load_saved_progress(
            [image_files['a.jpg']])
        assert remaining == [image_files['a.jpg']]
        assert done == set()
        assert hashes == {}
        # Stale progress file is cleared
        assert worker.progress_manager.load_progress() is None

    def test_stop_requests_pause_and_save(self, temp_dir, image_files):
        w = workers.ImageComparisonWorker(
            folder=str(temp_dir), keep_better_quality=False,
            preserve_metadata=False, progress_file=temp_dir / 'p.bin')
        calls = []
        w._save_progress = lambda state, *args: calls.append(state)
        # Stop once the scan finishes — before the first processing batch
        original_scan = w._get_image_files

        def scan_then_stop(folder):
            files = original_scan(folder)
            w.stop()
            return files

        w._get_image_files = scan_then_stop
        w.run()
        assert workers.ProgressState.PAUSED in calls
        assert _last_emission(w.signals.paused) is not None


# ---------------------------------------------------------------------------
# Error handling — network drives & special folders
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Tests for filesystem error handling."""

    def test_describe_permission_error(self, worker):
        err = PermissionError(13, 'denied', '/root/secret')
        assert 'Access denied' in worker._describe_fs_error(err)

    def test_describe_network_error(self, worker):
        err = OSError(67, 'network name not found')
        err.winerror = 67
        assert 'Network drive is not accessible' in worker._describe_fs_error(err)

    def test_describe_not_found(self, worker):
        err = FileNotFoundError(2, 'missing', '/gone')
        assert 'Folder not found' in worker._describe_fs_error(err)

    def test_describe_generic(self, worker):
        assert worker._describe_fs_error(OSError('weird')) == 'weird'

    def test_check_folder_access_ok(self, worker):
        assert worker._check_folder_access() is None

    def test_check_folder_access_missing(self, worker, temp_dir):
        worker.folder = str(temp_dir / 'missing')
        assert 'not found' in worker._check_folder_access().lower()

    def test_walk_error_counted(self, worker):
        worker._on_walk_error(PermissionError(13, 'denied', '/locked'))
        assert worker.metrics.inaccessible_dirs == 1

    def test_run_missing_directory(self, temp_dir):
        w = workers.ImageComparisonWorker(
            folder=str(temp_dir / 'missing'), progress_file=temp_dir / 'p.bin')
        w.run()
        assert _last_emission(w.signals.error) is not None
        assert w.signals.finished.emissions == []

    def test_run_empty_directory(self, worker):
        worker.run()
        msg, dups = _last_emission(worker.signals.finished)
        assert 'No image files' in msg
        assert dups == {}


# ---------------------------------------------------------------------------
# End-to-end run()
# ---------------------------------------------------------------------------

class TestRun:
    """Integration tests for the worker run() method."""

    def _stub_hashing(self, hash_for_size):
        """Stub WandImage+imagehash so same-size files share a hash."""
        def fake_wand(filename=None):
            return FakeWandImage(filename=filename)
        return fake_wand

    def test_run_finds_duplicates(self, worker, image_files):
        fake_wand = self._stub_hashing(None)
        with patch.object(workers, 'WandImage', fake_wand), \
             patch.object(workers.imagehash, 'phash',
                          side_effect=lambda img: f'ph{len(img)}'), \
             patch.object(workers.imagehash, 'average_hash', return_value='ah'):
            worker.run()

        msg, dups = _last_emission(worker.signals.finished)
        assert len(dups) == 2  # a+b (100b) and d+e (80b)
        # Metrics were emitted
        metrics = _last_emission(worker.signals.metrics_ready)[0]
        assert metrics['total_files'] == 5
        assert metrics['hashed_files'] == 4  # c.jpg filtered out by size
        # Progress file cleared after completion
        assert not worker.progress_manager.progress_file.exists()
        # Progress reached 100
        assert worker.signals.progress.emissions[-1] == (100,)

    def test_run_without_size_check_hashes_all(self, worker, image_files):
        worker.use_file_size = False
        fake_wand = self._stub_hashing(None)
        with patch.object(workers, 'WandImage', fake_wand), \
             patch.object(workers.imagehash, 'phash',
                          side_effect=lambda img: f'ph{len(img)}'), \
             patch.object(workers.imagehash, 'average_hash', return_value='ah'):
            worker.run()
        metrics = _last_emission(worker.signals.metrics_ready)[0]
        assert metrics['hashed_files'] == 5

    def test_run_no_potential_duplicates(self, worker, temp_dir):
        for f in temp_dir.glob('*.jpg'):
            f.unlink()
        (temp_dir / 'one.jpg').write_bytes(b'x' * 10)
        (temp_dir / 'two.jpg').write_bytes(b'y' * 20)
        worker.run()
        msg, dups = _last_emission(worker.signals.finished)
        assert 'No potential duplicates' in msg
        assert dups == {}

    def test_run_resume_from_saved_progress(self, worker, image_files):
        manager = workers.ProgressManager(worker.progress_manager.progress_file)
        # Pre-seed progress: a.jpg already hashed
        manager.save_progress(workers.ProgressData(
            state=workers.ProgressState.PAUSED,
            folder=worker.folder,
            recursive=worker.recursive,
            processed_files=[image_files['a.jpg']],
            remaining_files=[image_files['b.jpg'], image_files['d.jpg'],
                             image_files['e.jpg']],
            hashes={'h1:h1': [image_files['a.jpg']]},
        ))
        fake_wand = self._stub_hashing(None)
        with patch.object(workers, 'WandImage', fake_wand), \
             patch.object(workers.imagehash, 'phash',
                          side_effect=lambda img: f'ph{len(img)}'), \
             patch.object(workers.imagehash, 'average_hash', return_value='ah'):
            worker.run()
        metrics = _last_emission(worker.signals.metrics_ready)[0]
        # a.jpg skipped via resume — only 3 hashed in this run
        assert metrics['hashed_files'] == 3
        assert _last_emission(worker.signals.progress_loaded) == (True,)
