Configuration
=============

Main Options
-----------

1. **Comparison Precision**
   - Precision level (1-100):
     * Lower values find more duplicates
     * Higher values find only nearly identical duplicates

2. **Minimum Sizes**
   - Ignore images below:
     * Minimum width (pixels)
     * Minimum height (pixels)
     * Minimum size (KB)

3. **Supported Formats**
   - Allowed extensions:
     * .jpg, .jpeg
     * .png
     * .gif
     * .bmp
     * .webp

4. **Excluded Folders**
   - List of folders to ignore:
     * System folders
     * Temporary folders
     * Specific folders

5. **Processing Options**
   - Number of threads:
     * Increase for better performance
     * Decrease to save resources
   - Cache size:
     * Maximum memory for cache (MB)

6. **Output Options**
   - Generate reports:
     * PDF
     * CSV
     * JSON
   - Save logs:
     * Detail level
     * File location

7. **User Interface**
   - Language:
     * Italian
     * English
   - Theme:
     * Light
     * Dark

8. **Advanced**
   - Comparison algorithm:
     * Average Hash
     * Perceptual Hash
     * Difference Hash
   - Optimizations:
     * Image pre-loading
     * Results buffering

Configuration Tips
-----------------

1. **Performance**
   - Use more threads on multi-core systems
   - Increase cache on systems with ample RAM

2. **Precision**
   - Level 70-80 for good balance
   - Level 90+ for very strict comparisons

3. **Memory**
   - Monitor RAM usage
   - Reduce cache if needed

4. **Backup**
   - Always save configurations
   - Export reports before deleting images
