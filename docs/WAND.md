# Wand / ImageMagick Integration

This document describes the Wand (ImageMagick) specific features used by
Images-Deduplicator, how the image processing pipeline works, and the known
limitations.

## Why Wand

The project uses [Wand](https://docs.wand-py.org/) — a Python binding for
ImageMagick — instead of Pillow for all image decoding, preview and metadata
operations. Wand provides:

- Native support for a wide range of formats (JPEG, PNG, TIFF, WEBP, PSD, GIF,
  BMP and others supported by the installed ImageMagick build).
- Reliable handling of large and complex image files.
- Consistent EXIF/metadata access through `img.metadata`.

## Prerequisites

Wand requires **ImageMagick** to be installed on the system. Wand is only the
binding — all decoding is done by the ImageMagick shared libraries.

| OS | Installation |
| --- | --- |
| Windows | [imagemagick.org installer][im-win] |
| macOS | `brew install imagemagick` |
| Linux | `sudo apt-get install libmagickwand-dev` (Debian/Ubuntu) |

[im-win]: https://imagemagick.org/script/download.php#windows

If the shared library is not found, Wand raises
`ImportError: MagickWand shared library not found` on import.

## Supported formats

The scanner collects files with these extensions
(`SUPPORTED_IMAGE_EXTENSIONS` in `script/workers.py`):

```text
.jpg .jpeg .png .tiff .tif .webp .psd .gif .bmp
```

Format notes:

- **PSD** — ImageMagick reads the flattened composite layer; a PSD whose
  layers differ from the flattened preview may hash differently than expected.
- **GIF** — only the first frame is used for hashing and previews; animated
  GIFs are compared by their first frame.
- **TIFF / PSD** — multi-page/multi-image files are read via the first image
  in the sequence.
- **HEIC/HEIF, AVIF** — not in the supported extension list; can be enabled
  only if the local ImageMagick build ships the delegates and the extension
  list is extended.

## Comparison pipeline

The duplicate detection pipeline (`ImageComparisonWorker` in
`script/workers.py`) works in stages:

1. **Folder scan** — files with supported extensions are collected
   (optionally recursive). Inaccessible directories are counted and skipped
   with a warning instead of aborting the scan.
2. **File size comparison** *(optional detection method)* — files are grouped
   by byte size. Only size groups with 2+ files become candidates for hashing,
   which skips most of the work for large collections. Can be disabled in the
   UI ("Compare file sizes") to hash every file; in that case files with equal
   hashes are reported as duplicates regardless of size.
3. **Hashing** — for each candidate file:
   `WandImage → sRGB colorspace → PNG blob → PIL.Image → imagehash`.
   Two hashes are combined into a key: `phash:ahash` (perceptual + average).
   Results are stored in `cache/image_hashes.json` (7-day expiry, keyed by
   file path + mtime).
4. **Batch processing** — candidates are processed in sequential batches
   (`batch_size`, 1–200, default 50). Each batch is hashed in a thread pool
   (`MAX_WORKERS = os.cpu_count()`), and progress is checkpointed between
   batches to `cache/scan_progress.bin`.
5. **Grouping** — combined-hash keys are clustered into **similarity
   groups**: keys whose mutual Hamming distance stays within the configured
   `similarity_threshold` (percent similarity of phash+ahash) are merged, so
   near-identical images group together even when they are not bit-identical.
   A threshold of 100 restores strict exact-match behavior. Files in each
   group are additionally validated by file size when size comparison is
   enabled. With "Keep better quality" enabled, each group is sorted by a
   composite quality score — pixel count, then the encoder quality estimate
   (e.g. JPEG quality), then file size — so the best copy leads the group;
   its metadata can optionally be copied from the duplicates it replaces.

## Progress saving and resuming

Long scans checkpoint progress to `cache/scan_progress.bin` after every
batch. If the app is closed mid-scan (or the worker is stopped), the next
scan of the same folder resumes from the saved state: already-hashed files
are skipped and the collected hash map is restored. The progress file is
removed automatically when a scan completes.

## Performance metrics

Each run collects metrics (`ComparisonMetrics`): total/hashed file counts,
cache hits/misses, errors, skipped directories, scan/hash/total time and
throughput (files/s). The summary is written to the log and emitted via the
`metrics_ready` signal.

## Metadata handling

- Extraction: `ImageMetadata.get_metadata()` reads format, dimensions,
  resolution, EXIF entries and format-specific fields via `img.metadata`.
- Preservation: `ImageMetadata.apply_metadata()` writes metadata back with
  ImageMagick (`img.save`) — only fields supported by the target format
  survive the round-trip.

## Known limitations

- **ImageMagick delegate coverage** — the readable format list depends on
  the delegates compiled into the local ImageMagick build.
- **Memory** — very large images are fully decoded into memory; multiple
  worker threads can multiply peak usage.
- **Vector formats** — SVG is not scanned (rasterization delegates vary).
- **Hashing needs a PNG re-encode** — every uncached file is re-encoded to
  PNG in memory for the hash library; this dominates hashing time for large
  files.
- **Metadata writes** — `apply_metadata()` does not guarantee lossless EXIF
  round-trips for every format; verify preserved fields for critical files.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `MagickWand library not found` | Install ImageMagick or set `MAGICK_HOME` |
| Crash on first `WandImage` use | 32/64-bit Python/ImageMagick mismatch |
| PSD/GIF hashing looks wrong | First frame compared — expected |
| "Network drive is not accessible" | UNC offline — reconnect the drive |
| "directories skipped" | Restricted folders excluded |

## Related documentation

- `PREREQUISITES.md` — installation instructions
- `api.md` — module-level API reference
- `STRUCTURE.md` — project layout
