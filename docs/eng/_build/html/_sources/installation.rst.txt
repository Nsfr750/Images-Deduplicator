Installation
============

Prerequisites
------------

Before installing Images Deduplicator, ensure you have:

1. Python 3.8 or higher (3.10+ recommended)
2. ImageMagick installed (required for Wand)
3. Git (optional, for development installation)

Installing ImageMagick
---------------------

Windows
~~~~~~~

1. Download the latest ImageMagick installer from the `official website <https://imagemagick.org/script/download.php#windows>`_
2. Run the installer with these options:
   - Check "Install development headers and libraries for C and C++"
   - Check "Add application directory to your system path"
3. Verify installation by opening a new command prompt and running:

   .. code-block:: bash

      magick --version

macOS
~~~~~

.. code-block:: bash

   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install ImageMagick
   brew install imagemagick

Linux (Debian/Ubuntu)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y \
       imagemagick \
       libmagickwand-dev \
       libmagickcore-dev

Installation via pip
-------------------

The recommended way to install Images Deduplicator is using pip:

.. code-block:: bash

   # Install the package
   pip install images-deduplicator
   
   # Run the application
   images-dedup

Installation from Source
-----------------------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator

2. Install in development mode with all dependencies:

.. code-block:: bash

   # Create and activate a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install package in development mode with all extras
   pip install -e '.[dev,docs,packaging]'

3. Run the application:

.. code-block:: bash

   python main.py

Verifying the Installation
-------------------------

To verify that Wand can find and use ImageMagick:

.. code-block:: python

   from wand.image import Image
   from wand.version import QUANTUM_DEPTH, MAGICK_VERSION
   
   print(f"ImageMagick version: {MAGICK_VERSION}")
   print(f"Quantum depth: {QUANTUM_DEPTH} bits")
   
   # Test basic image operations
   with Image(filename='wizard:') as img:
       print(f'Image size: {img.size}')

Troubleshooting
--------------

**Wand can't find ImageMagick**

If you encounter errors about missing libraries:

1. Ensure ImageMagick is properly installed and in your system PATH
2. On Windows, you may need to restart your terminal/IDE after installation
3. Verify the installation by running ``magick --version`` in your terminal

**Permission Errors**

If you encounter permission errors, try:

.. code-block:: bash

   # On Linux/macOS
   pip install --user images-deduplicator
   
   # Or use a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .

**Memory Issues**

For large image collections, you might need to increase ImageMagick's resource limits. Create or edit the ``policy.xml`` file:

- Linux/macOS: ``/etc/ImageMagick-7/policy.xml``
- Windows: ``C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\policy.xml``

And adjust these values:

.. code-block:: xml

   <policy domain="resource" name="width" value="16KP"/>
   <policy domain="resource" name="height" value="16KP"/>
   <policy domain="resource" name="area" value="128MB"/>
   <policy domain="resource" name="memory" value="4GiB"/>
   <policy domain="resource" name="map" value="8GiB"/>
   <policy domain="resource" name="disk" value="16GiB"/>
