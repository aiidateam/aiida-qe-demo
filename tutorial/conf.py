# outline for a myst_nb project with sphinx
# build with: sphinx-build -nW --keep-going -b html . ./_build/html

# specify project details
project = "AiiDA Demonstration"
author = "The AiiDA team."
copyright = f"2022 AiiDA. All Rights Reserved"
master_doc = "index"

# load extensions
extensions = [
    "myst_nb",
    "sphinx_design",
    "sphinx_subfigure",
]

myst_enable_extensions = ["colon_fence", "deflist", "attrs_image"]

# basic build settings
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]
nitpicky = True

html_theme = "sphinx_book_theme"
html_logo = "_static/logo-light.svg"
html_title = "Demonstration"  # shown below logo
html_favicon = "_static/favicon-32x32.png"

html_theme_options = {
    "repository_url": "https://github.com/chrisjsewell/aiida-qe-demo",
    "repository_branch": "main",
    "path_to_docs": "tutorial",
    "use_download_button": True,
    "launch_buttons": {
        "notebook_interface": "jupyterlab",
        "binderhub_url": "https://mybinder.org",
        # "colab_url": "https://colab.research.google.com/",
    },
    "use_sidenotes": True,
    # "announcement": "This tutorial is in development!",
    "extra_navbar": "",
}

## myst_nb default settings

# Custom formats for reading notebook; suffix -> reader
# nb_custom_formats = {}

# Notebook level metadata key for config overrides
# nb_metadata_key = 'mystnb'

# Cell level metadata key for config overrides
# nb_cell_metadata_key = 'mystnb'

# Mapping of kernel name regex to replacement kernel name(applied before execution)
# nb_kernel_rgx_aliases = {}

# Execution mode for notebooks
nb_execution_mode = "cache"

# Path to folder for caching notebooks (default: <outdir>)
# nb_execution_cache_path = ''

# Exclude (POSIX) glob patterns for notebooks
# nb_execution_excludepatterns = (
#     "bands_workflow.ipynb",
# )

# Execution timeout (seconds)
nb_execution_timeout = 600

# Use temporary folder for the execution current working directory
# nb_execution_in_temp = False

# Allow errors during execution
# nb_execution_allow_errors = False

# Raise an exception on failed execution, rather than emitting a warning
# nb_execution_raise_on_error = False

# Print traceback to stderr on execution error
import os

nb_execution_show_tb = nb_execution_show_tb = "READTHEDOCS" in os.environ

# Merge stdout/stderr execution output streams
nb_merge_streams = True

# The entry point for the execution output render class (in group `myst_nb.output_renderer`)
# nb_render_plugin = 'default'

# Remove code cell source
# nb_remove_code_source = False

# Remove code cell outputs
# nb_remove_code_outputs = False

# Number code cell source lines
# nb_number_source_lines = False

# Overrides for the base render priority of mime types: list of (builder name, mime type, priority)
# nb_mime_priority_overrides = ()

# Behaviour for stderr output
# nb_output_stderr = 'show'

# Pygments lexer applied to stdout/stderr and text/plain outputs
# nb_render_text_lexer = 'myst-ansi'

# Pygments lexer applied to error/traceback outputs
# nb_render_error_lexer = 'ipythontb'

# Options for image outputs (class|alt|height|width|scale|align)
# nb_render_image_options = {}

# Options for figure outputs (classes|name|caption|caption_before)
# nb_render_figure_options = {}

# The format to use for text/markdown rendering
# nb_render_markdown_format = 'commonmark'

# Javascript to be loaded on pages containing ipywidgets
# nb_ipywidgets_js = {'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js': {'integrity': 'sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=', 'crossorigin': 'anonymous'}, 'https://unpkg.com/@jupyter-widgets/html-manager@^0.20.0/dist/embed-amd.js': {'data-jupyter-widgets-cdn': 'https://cdn.jsdelivr.net/npm/', 'crossorigin': 'anonymous'}}

nb_code_prompt_show = "Show cell {type}"
nb_code_prompt_hide = "Hide cell {type}"
