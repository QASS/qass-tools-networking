import os
import sys
import pathlib
sys.path.insert(0, os.path.abspath('../src'))
#sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
sys.path.append(os.path.abspath("./_ext"))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Qass Tools Networking'
copyright = '2022, QASS GmbH'
author = 'QASS GmbH'
release = '3.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'enum_tools.autoenum',
              'sphinx.ext.coverage', 'sphinx.ext.napoleon', 'sphinx_design',]
              #'autointenum']

templates_path = ['_templates']
exclude_patterns = []
rst_prolog = """
.. role:: AnalyzerVersion 
.. role:: Contributor
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_logo = "./QASS_Logo_neu.svg"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'prev_next_buttons_location': 'both',
    'logo_only': False }