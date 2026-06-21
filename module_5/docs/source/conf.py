"""Sphinx configuration for the Grad Cafe analytics service."""

import os
import sys

# docs/source is two levels below module_4, which contains the src package.
sys.path.insert(0, os.path.abspath("../.."))

project = "Grad Cafe Analytics"
copyright = "2026, Rida Fatima Alvi"
author = "Rida Fatima Alvi"
release = "1.0"

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
