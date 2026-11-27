# API Reference

Detailed documentation of the Images-Deduplicator internal API. The
application is a PyQt6 desktop app; this reference covers the modules under
`script/` for contributors and integrators.

## Image Processing — `script/workers.py`

The comparison pipeline lives here: folder scanning, hashing, similarity
grouping, batching, caching, progress persistence and metrics.

### `ImageComparisonWorker(QRunnable)`

Background worker that finds duplicate images in a folder.

```python
worker = ImageComparisonWorker(
    folder: str,
    recursive: bool = True,
    similarity_threshold: int = 85,
    keep_better_quality: bool = True,
    preserve_metadata: bool = True,
    batch_size: int = 50,
    use_file_size: bool = True,
    progress_file: str | Path | None = None,
)
```

| Parameter | Description |
| --- | --- |
| `folder` | Folder to scan |
| `recursive` | Include subdirectories |
| `similarity_threshold` | Min similarity % to cluster (100 = exact) |
| `keep_better_quality` | Best-quality image leads each group |
| `preserve_metadata` | Copy metadata from duplicates onto the best image |
| `batch_size` | Images per processing batch (1–200) |
| `use_file_size` | File size comparison as extra detection method |
| `progress_file` | Checkpoint path (default `cache/scan_progress.bin`) |

Public attributes:

- `metrics: ComparisonMetrics` — collected during the run
- `quality_scores: Dict[str, Tuple[int, int, int]]` — leading image scores
- `is_running` / `stop()` — cooperative cancellation

Signals (`worker.signals`):

| Signal | Payload | Emitted when |
| --- | --- | --- |
| `progress` | `int` | Progress percentage changes |
| `finished` | `str, dict` | Run completes (message, duplicates map) |
| `error` | `str` | Fatal error |
| `paused` | — | Processing stopped and progress saved |
| `progress_saved` | `str` | A progress checkpoint was written |
| `progress_loaded` | `bool` | Saved progress was resumed |
| `state_changed` | `str` | Progress state name changed |
| `metrics_ready` | `dict` | Final metrics are available |

Result shape: `duplicates = {original_path: [dup_path, ...]}` — the leading
image of each similarity group is the key; the rest are its duplicates.

### `HashCache`

On-disk JSON cache of per-image hashes (`cache/image_hashes.json`, 7-day
expiry, invalidated on file mtime).

```python
cache = HashCache(cache_file: Path = CACHE_FILE)
cache.get(file_path)          # -> {'phash','ahash','mtime','timestamp'} | None
cache.set(file_path, phash, ahash)
cache.save()                  # persist to disk
cache.cleanup()               # drop expired entries
```

### `ProgressManager` / `ProgressData` / `ProgressState`

Checkpoint persistence for resumable scans.

```python
pm = ProgressManager(progress_file="cache/scan_progress.bin")
pm.save_progress(data: ProgressData) -> bool
pm.load_progress() -> ProgressData | None
pm.clear_progress() -> bool
```

`ProgressData` fields: `state`, `folder`, `recursive`, `processed_files`,
`remaining_files`, `hashes`, `duplicates`, `current_batch`, `total_files`,
`processed_count`, `start_time`, `end_time`, `error_message`.
`ProgressState` values: `NOT_STARTED`, `SCANNING`, `PROCESSING`, `COMPLETED`,
`PAUSED`, `ERROR`.

### `ComparisonMetrics`

Per-run performance counters: `total_files`, `size_filtered_files`,
`hashed_files`, `cache_hits`, `cache_misses`, `errors`, `inaccessible_dirs`,
`scan_time_seconds`, `hash_time_seconds`, `total_time_seconds`,
`files_per_second`, `to_dict()`.

### `ImageMetadata`

Static helpers for metadata via Wand:

- `get_metadata(image_path) -> dict` — format, dimensions, resolution,
  EXIF entries and format-specific fields; `{}` on failure
- `apply_metadata(image_path, metadata) -> bool` — write metadata back
  through ImageMagick

## Main Window — `script/UI.py`

### `UI(QMainWindow)`

```python
window = UI(config: dict, lang: str = 'en')
```

Owns the main window, the `thread_pool` (`QThreadPool`), the
`UndoManager`, the `LanguageManager` and the `MenuManager`. Comparison is
started by `compare_images()` which constructs `ImageComparisonWorker` from
the current UI options and connects its signals.

Key methods: `browse_folder`, `compare_images`, `on_comparison_finished`,
`update_duplicates_list`, `update_preview`, `delete_selected`,
`delete_all_duplicates`, `apply_style`, `apply_theme`.

## Undo — `script/undo_manager.py`

### `FileOperation` (dataclass)

`operation_type` (`'delete'|'move'`), `source`, `destination`,
`metadata`, `timestamp`, `backup_path`. `undo()` restores the file (delete
operations restore a timestamped backup from `.image_dedup_backups/`).

### `UndoManager`

```python
um = UndoManager(max_history=100)
um.add_operation(op: FileOperation)
um.can_undo() -> bool
um.get_last_operation() -> FileOperation | None
um.undo_last_operation() -> bool
um.clear()
um.move_to_trash(file_path) -> str
```

## Internationalization — `language_manager.py` + `translations.py`

### `LanguageManager(QObject)`

```python
lm = LanguageManager(default_lang='en')
lm.current_language -> str          # property
lm.available_languages -> dict      # {'en': 'English', 'it': 'Italiano'}
lm.set_language(lang_code) -> bool
lm.translate(key, **kwargs) -> str
lm.language_changed                 # pyqtSignal(str)
```

`script/translations.py` holds the `TRANSLATIONS` dict and `LANGUAGES`;
`t(key, lang='en', **kwargs)` is kept for backward compatibility.

## Updates — `script/updates.py`

`UpdateChecker(QObject)` checks GitHub releases for newer versions:
`check_for_updates(force_check=False)`; emits signals for result states.
`check_for_updates(parent, current_version, language_manager)` is the
convenience entry point that also shows the update dialog.

## Version — `script/version.py`

`__version__`, `get_version()`, `get_version_info()`,
`check_version_compatibility(min_version)`, `get_versions()`.

## Dialogs and helpers

| Module | Public API |
| --- | --- |
| `script/about.py` | `AboutDialog`, `get_wand_version_info()` |
| `script/menu.py` | `MenuManager` — menubar, actions, shortcuts |
| `script/settings_dialog.py` | `SettingsDialog`, `get_settings()` |
| `script/log_viewer.py` | `LogViewer` — log browsing/filtering dialog |
| `script/help.py` | `HelpDialog` — searchable help with dark theme |
| `script/sponsor.py` | `SponsorDialog` — donation links |
| `script/empty_trash.py` | `empty_system_trash(lang)` -> `(bool, str)` |
| `script/image_dialog_preview.py` | `show_image_preview()` — zoomable |
| `script/update_preview.py` | `update_preview()` — preview refresh |
| `script/styles.py` | `setup_styles`, `apply_theme`, `apply_style` |
| `script/logger.py` | `logger` — the application logger |

## Usage examples

### Programmatic scan

```python
from PyQt6.QtCore import QThreadPool
from script.workers import ImageComparisonWorker

worker = ImageComparisonWorker(
    folder="/photos",
    similarity_threshold=90,
    use_file_size=True,
    batch_size=100,
)
worker.signals.finished.connect(
    lambda msg, dups: print(msg, len(dups), "groups"))
worker.signals.metrics_ready.connect(print)
QThreadPool.globalInstance().start(worker)
```

### Undo a deletion

```python
from script.undo_manager import UndoManager, FileOperation

um = UndoManager()
um.add_operation(FileOperation(operation_type='delete', source='/tmp/dup.jpg'))
if um.can_undo():
    um.undo_last_operation()
```

## Testing

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes (follow PEP8 / black)
4. Add tests under `tests/`
5. Submit a pull request

## License

GPLv3 — see `LICENSE` for details.
