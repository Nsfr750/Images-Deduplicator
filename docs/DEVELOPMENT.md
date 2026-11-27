# Developer Documentation

Guide for contributing to Images-Deduplicator.

## Setup

1. Install ImageMagick (see `PREREQUISITES.md` for per-OS commands).
2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

3. Run the app: `python main.py`.

## Project layout

See `docs/STRUCTURE.md` for the full tree. The important pieces:

| Path | Role |
| --- | --- |
| `main.py` | Entry point — builds `QApplication` + `UI` |
| `script/UI.py` | Main window, starts workers on `QThreadPool` |
| `script/workers.py` | Scan/hash/group pipeline, cache, progress, metrics |
| `script/undo_manager.py` | Undoable file operations |
| `script/language_manager.py` | i18n runtime (en, it) |
| `script/translations.py` | Translation strings |
| `script/version.py` | SemVer components |
| `tests/` | pytest suite |

## Conventions

- **Style**: PEP8, formatted with `black`; type hints on new code.
- **UI**: PyQt6 only; long work goes in `QRunnable` workers, never the
  GUI thread; signal wiring via `pyqtSignal`.
- **Images**: Wand/ImageMagick for all decoding and metadata — never
  Pillow.
- **Strings**: no hardcoded UI text — add keys to
  `script/translations.py` for every language (`en`, `it`); never `.json`
  language files.
- **Docs**: new functions/classes get docstrings; behavior changes update
  `CHANGELOG.md` and `docs/`.
- **Versioning**: `script/version.py` follows SemVer 2.0.0.

## Comparison pipeline internals

`ImageComparisonWorker.run()` stages:

1. `_get_image_files` — extension-filtered scan (`os.walk` with
   `onerror` collecting inaccessible dirs).
2. File size prefilter (`use_file_size`) — `_group_files_by_size`, sizes
   cached in `self._file_sizes`.
3. `_load_saved_progress` — resume previous checkpoint if the folder
   matches.
4. Batch loop — `_iter_batches(batch_size)`; chunks hashed in a
   `ThreadPoolExecutor`; `_save_progress` checkpoint after each batch.
5. `_get_image_hashes` — `WandImage → sRGB → PNG → PIL → imagehash`
   (`phash:ahash` combined key), cached in `HashCache`.
6. `_group_by_similarity` — union-find clustering of hash keys by
   Hamming distance within `similarity_threshold`.
7. `_process_duplicates` — per group: optional size validation,
   composite quality sort `(resolution, encoder quality, size)`,
   optional metadata preservation.
8. `metrics_ready` + `finished` signals; progress file cleared.

## Extending

### Adding a translation

1. Add the key under both `en` and `it` in `script/translations.py`.
2. Use `self.lang_manager.translate('key')` (or `t('key', lang)`).

### Adding a new scan option

1. Add a `QCheckBox` in `UI.init_ui` (options frame) + translation keys.
2. Pass the flag to `ImageComparisonWorker` in `compare_images`.
3. Consume the parameter inside the worker (`workers.py`).

### Writing tests

- Tests live in `tests/`; run with `pytest tests/`.
- `tests/test_workers_wand.py` shows how to stub heavy deps
  (`wand`, `PyQt6`, `imagehash`, `PIL`) via `sys.modules` so pipeline
  logic can be tested headless; stubs are installed only for the import
  of `workers` and restored afterwards.
- `isolated_hash_cache` fixture redirects the default hash cache to a
  temp path — do not write to `cache/` from tests.

## Debugging

- Logs: `logs/image_dedup_*.log` (DEBUG level by default).
- Metrics of each run are logged at completion and emitted via
  `metrics_ready` — check `cache_hits`/`files_per_second` when tuning.
- `cache/scan_progress.bin` — delete it to force a fresh scan.

## Release checklist

1. `black script/ tests/`
2. `pytest tests/`
3. Update `CHANGELOG.md`, bump `script/version.py`
4. Update `TO_DO.md`
