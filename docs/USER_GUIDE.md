# User Guide

Step-by-step guide to finding and removing duplicate images with
Images-Deduplicator.

## First run

1. Install ImageMagick (required — see `PREREQUISITES.md`).
2. Launch the application:

   ```bash
   python main.py
   ```

3. Pick the interface language from the language menu (English or
   Italiano).

## Scanning for duplicates

1. Click **Browse** and select the folder to scan (you can also drag a
   folder onto the field).
2. Configure the scan options:

   | Option | Effect |
   | --- | --- |
   | **Search Subfolders** | Include nested directories |
   | **Keep better quality** | Highest-quality image leads each group |
   | **Preserve metadata** | Copy metadata from duplicates onto the best image |
   | **Compare file sizes** | Extra method — faster, needs same size |

3. Click **Compare** and wait for the scan. A progress bar shows the
   current stage.

### How detection works

The app hashes every candidate image (perceptual + average hash) and
clusters hashes whose similarity is within the configured threshold — so
near-identical photos are grouped even if they are not bit-identical.
Files already hashed in a previous run are served from the local cache.

### Interrupted scans

Long scans save progress automatically after each batch
(`cache/scan_progress.bin`). If you close the app mid-scan, just run the
same folder again — hashing resumes where it stopped.

## Reviewing results

The **Duplicates found** list shows every duplicate file; the first image
of each group is considered the original (or the best-quality copy when
"Keep better quality" is enabled).

- Select items in the list to preview them (zoom supported via the
  preview dialog).
- Use **Select All** / **Select None** for bulk selection.

## Deleting duplicates

| Button | Behavior |
| --- | --- |
| **Delete Selected** | Moves the selected files to the system trash |
| **Delete All Duplicates** | Moves every listed duplicate to trash |

Both actions ask for confirmation first. Deletions are recorded by the
Undo manager — use the undo action (Edit menu / Ctrl+Z) to restore
recently removed files.

## Understanding messages

- **"Network drive is not accessible"** — the folder is on an offline UNC
  share; reconnect the drive.
- **"N directories were skipped — access denied"** — restricted folders
  were excluded from the scan; the count appears in the status bar and
  in the completion message.

## Checking versions

**Help → About** shows the app version plus Python, Qt, PyQt, **Wand** and
**ImageMagick** versions — useful when reporting issues.

## Logs

**Tools → Log viewer** opens the application logs with level filtering.
Logs live in the `logs/` directory; attach the latest file when opening a
bug report.
