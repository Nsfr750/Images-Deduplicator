import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'Images Deduplicator'
author = 'Nsfr750'
copyright = '2025, Nsfr750'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'myst_parser',
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

myst_heading_anchors = 3

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
if not os.path.exists('_static'):
    os.makedirs('_static')
