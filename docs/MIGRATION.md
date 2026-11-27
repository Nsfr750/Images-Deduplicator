# Migration Guide: Pillow → Wand

The project migrated image decoding and metadata handling from
Pillow (PIL) to [Wand](https://docs.wand-py.org/) — the ImageMagick
binding — in version 1.6.0. This guide explains what changed, why, and
how to port code that still uses Pillow.

## Why the migration

| Aspect | Pillow | Wand (ImageMagick) |
| --- | --- | --- |
| Formats | Common formats | ImageMagick delegates (PSD, TIFF, GIF, BMP) |
| PSD | Not supported | Flattened composite supported |
| Large files | Decodes to memory | Streams through ImageMagick |
| Metadata | `img.info` / `getexif()` | Uniform `img.metadata` map |
| License | MIT (PIL fork HPND) | MIT |

## System dependency

Pillow is pure Python; **Wand needs ImageMagick installed on the system** —
see `docs/PREREQUISITES.md` for per-OS install commands. If the shared
library is missing, `import wand` raises
`ImportError: MagickWand shared library not found`.

## API mapping

Common operations and their Wand equivalents:

```python
# Pillow                              # Wand
from PIL import Image                 from wand.image import Image as WandImage

img = Image.open(path)                with WandImage(filename=path) as img:
img.width, img.height                     img.width, img.height
img.format                                img.format
img.mode                                  img.colorspace
img.convert('RGB')                        img.transform_colorspace('srgb')
img.save(out_path)                        img.save(filename=out_path)
img.save(buf, format='PNG')               img.format = 'png'; img.save(file=buf)
img.info.get('dpi')                       img.metadata.get('dpi')
img.getexif()[tag]                        img.metadata.get(f'exif:{tag}')
Image.open(BytesIO(data))                 WandImage(blob=data)
```

Key differences:

- **Context manager** — always use `with WandImage(...) as img:` so the
  native resources are released.
- **Colorspace vs mode** — normalize with
  `img.transform_colorspace('srgb')` before hashing/converting.
- **Metadata** — a flat `img.metadata` dict; EXIF keys use the `exif:` prefix
  (`exif:Make`, `exif:Model`).

## How the pipeline changed

Duplicate hashing used to be `PIL.Image → imagehash`. It is now
`WandImage → sRGB → PNG blob → PIL.Image (in-memory) → imagehash`: Wand
decodes every supported format, the resulting PNG blob feeds the hash
library — one short PIL hop remains only inside
`ImageComparisonWorker._get_image_hashes()` as the imagehash input adapter.

## Deprecated identifiers

- `PILLOW_VERSION` in `script/version.py` was replaced by `WAND_VERSION`.
- No `ImageProcessor` class exists — the pipeline lives in
  `script/workers.py` (`ImageComparisonWorker`, `ImageMetadata`,
  `HashCache`).

## Porting checklist for downstream code

1. Replace `Image.open()` calls with `WandImage` context blocks.
2. Replace mode checks/conversions with `img.colorspace` /
   `transform_colorspace('srgb')`.
3. Map `img.info`/`getexif()` reads to `img.metadata` keys.
4. Wrap Wand usage in `try/except` — corrupt inputs raise
   `wand.exceptions.*` errors rather than Pillow exceptions.
5. Do not hold `WandImage` references beyond the `with` block.
