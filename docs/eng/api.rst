API Reference
============

This section provides detailed documentation for the Images Deduplicator API. The application is built with a modular architecture, with each module handling specific functionality.

Core Modules
------------

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: QMainWindow, QApplication

   Main application entry point and core functionality.

Image Processing
----------------

.. automodule:: script.image_processor
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Handles all image processing operations using Wand/ImageMagick.

   Key Features:
   - Supports all major image formats (JPEG, PNG, WEBP, PSD, etc.)
   - Perceptual hashing for duplicate detection
   - Memory-efficient processing of large images
   - EXIF and metadata handling

User Interface
-------------

.. automodule:: script.UI
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: Ui_MainWindow

   Main window and UI components built with PyQt6.

.. automodule:: script.menu
   :members:
   :undoc-members:
   :show-inheritance:

   Application menu and toolbar functionality.

.. automodule:: script.image_dialog_preview
   :members:
   :undoc-members:
   :show-inheritance:

   Image preview and comparison dialog.

Core Functionality
-----------------

.. automodule:: script.workers
   :members:
   :undoc-members:
   :show-inheritance:

   Background workers for non-blocking UI operations.

.. automodule:: script.undo_manager
   :members:
   :undoc-members:
   :show-inheritance:

   Manages undo/redo operations for file operations.

Internationalization
-------------------

.. automodule:: script.translations
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: script.language_manager
   :members:
   :undoc-members:
   :show-inheritance:

   Handles language switching and string translations.

Utilities
---------

.. automodule:: script.logger
   :members:
   :undoc-members:
   :show-inheritance:

   Centralized logging functionality.

.. automodule:: script.version
   :members:
   :undoc-members:
   :show-inheritance:

   Version management and update checking.

.. automodule:: script.about
   :members:
   :undoc-members:
   :show-inheritance:

   About dialog and application information.

.. automodule:: script.help
   :members:
   :undoc-members:
   :show-inheritance:

   Help system and documentation viewer.

.. automodule:: script.sponsor
   :members:
   :undoc-members:
   :show-inheritance:

   Sponsor and donation functionality.

.. automodule:: script.styles
   :members:
   :undoc-members:
   :show-inheritance:

   Application theming and styling.

Wand/ImageMagick Integration
---------------------------

The application uses the Wand library (a Python binding for ImageMagick) for all image processing tasks. Key features include:

- Support for 200+ image formats
- Advanced image manipulation capabilities
- Color profile and metadata handling
- Memory-efficient processing

Example usage:

.. code-block:: python

   from wand.image import Image
   
   def get_image_size(image_path):
       with Image(filename=image_path) as img:
           return img.width, img.height

For more information, see the `Wand documentation <https://docs.wand-py.org/>`_ and `ImageMagick documentation <https://imagemagick.org/script/documentation.php>`_.

Notes
-----

- All file operations are performed in a thread-safe manner
- Image processing operations are optimized for performance
- The application includes comprehensive error handling and logging
- For advanced usage, many functions accept additional keyword arguments that are passed to the underlying Wand/ImageMagick functions

For more detailed API documentation, consult the source code directly or use the "Show code" option in the generated documentation.
