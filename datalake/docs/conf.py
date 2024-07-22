# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
from recommonmark.parser import CommonMarkParser
from datalake.config import settings

project = 'yelp dataset'
copyright = '2024, Praveer Kumar'
author = 'Praveer Kumar'
release = '0.1.0'
source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']

extensions = [
  "sphinx.ext.todo",
  "sphinx.ext.mathjax",
  "sphinx.ext.autodoc",
  "sphinx.ext.autosectionlabel",
  "sphinxcontrib.plantuml",
]
# PlantUML settings
jar_file = os.path.basename(settings.DOCS.PLANTUML_JAR)
local_jar_file = os.path.join("../../", settings.DOCS.CACHE_DIR, jar_file)
plantuml = f"java -jar {os.path.abspath(local_jar_file)}"
plantuml_output_format = "png"
plantuml_output_dir = "./_static/diagrams"

templates_path = ['_templates']
exclude_patterns = []
sources = [settings.DOCS.SOURCE_DIR]
build = [settings.DOCS.BUILD_DIR]

pygments_style = "default"
pygments_dark_style = "lightbulb"

todo_include_todos = True
autosectionlabel_prefix_document = True

html_title = settings.DOCS.TITLE
html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
    'custom.css',
]
html_static_path = ["_static"]
htmlhelp_basename = f'{settings.DOCS.DESCRIPTION}'
html_show_sphinx = False