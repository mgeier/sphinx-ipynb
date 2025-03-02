import os

# You can use sphinx-quickstart to create your own conf.py file!
# After that, you have to edit a few things.  See below.

# Select nbsphinx and, if needed, other Sphinx extensions:
extensions = [
    'nbsphinx',
    'sphinxcontrib.bibtex',  # for bibliographic references
    'sphinxcontrib.rsvgconverter',  # for SVG->PDF conversion in LaTeX output
    'sphinx_last_updated_by_git',  # get "last updated" from Git
    'sphinx_codeautolink',  # automatic links from code to documentation
    'sphinx.ext.intersphinx',  # links to other Sphinx projects (e.g. NumPy)
]

# These projects are also used for the sphinx_codeautolink extension:
intersphinx_mapping = {
    'IPython': ('https://ipython.readthedocs.io/en/stable/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'python': ('https://docs.python.org/3/', None),
}

# Don't add .txt suffix to source files:
html_sourcelink_suffix = ''

# List of arguments to be passed to the kernel that executes the notebooks:
nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
]

# Environment variables to be passed to the kernel:
os.environ['MY_DUMMY_VARIABLE'] = 'Hello from conf.py!'

nbsphinx_thumbnails = {
    'gallery/thumbnail-from-conf-py': 'gallery/a-local-file.png',
    'gallery/*-rst': 'images/notebook_icon.png',
    'orphan': '_static/favicon.svg',
}

# This is processed by Jinja2 and inserted before each notebook
nbsphinx_prolog = r"""
{% set docname = 'doc/' + env.doc2path(env.docname, base=None)|string %}

.. raw:: html

    <div class="admonition note">
      This page was generated from
      <a class="reference external" href="https://github.com/spatialaudio/nbsphinx/blob/{{ env.config.release|e }}/{{ docname|e }}">{{ docname|e }}</a>.
      Interactive online version:
      <span style="white-space: nowrap;"><a href="https://mybinder.org/v2/gh/spatialaudio/nbsphinx/{{ env.config.release|e }}?filepath={{ docname|e }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>.</span>
      <a href="{{ env.docname.split('/')|last|e + '.ipynb' }}" class="reference download internal" download>Download notebook</a>.
      <script>
        if (document.location.host) {
          let nbviewer_link = document.createElement('a');
          nbviewer_link.setAttribute('href',
            'https://nbviewer.org/url' +
            (window.location.protocol == 'https:' ? 's/' : '/') +
            window.location.host +
            window.location.pathname.slice(0, -4) +
            'ipynb');
          nbviewer_link.innerHTML = 'Or view it on <em>nbviewer</em>';
          nbviewer_link.classList.add('reference');
          nbviewer_link.classList.add('external');
          document.currentScript.replaceWith(nbviewer_link, '.');
        }
      </script>
    </div>

.. raw:: latex

    \nbsphinxstartnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{The following section was generated from
    \sphinxcode{\sphinxupquote{\strut {{ docname | escape_latex }}}} \dotfill}}
"""

# This is processed by Jinja2 and inserted after each notebook
nbsphinx_epilog = r"""
{% set docname = 'doc/' + env.doc2path(env.docname, base=None)|string %}
.. raw:: latex

    \nbsphinxstopnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{\dotfill\ \sphinxcode{\sphinxupquote{\strut
    {{ docname | escape_latex }}}} ends here.}}
"""

mathjax3_config = {
    'tex': {'tags': 'ams', 'useLabelIds': True},
}

# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html
bibtex_bibfiles = ['references.bib']
bibtex_reference_style = 'author_year'

# Support for notebook formats other than .ipynb
nbsphinx_custom_formats = {
    '.pct.py': ['jupytext.reads', {'fmt': 'py:percent'}],
    '.md': ['jupytext.reads', {'fmt': 'Rmd'}],
}

# Import Matplotlib to avoid this message in notebooks:
# "Matplotlib is building the font cache; this may take a moment."
import matplotlib.pyplot

# -- The settings below this line are not specific to nbsphinx ------------

master_doc = 'index'

project = 'nbsphinx'
author = 'Matthias Geier'
copyright = '2020, ' + author
html_show_copyright = False

linkcheck_ignore = [
    r'http://localhost:\d+/',
    'https://github.com/spatialaudio/nbsphinx/compare/',
    # 418 Client Error: Unknown for url: https://ieeexplore.ieee.org/document/5582063/
    'https://doi.org/10.1109/MCSE.2010.119',
    # Intermittent network errors:
    # Failed to establish a new connection: [Errno 101] Network is unreachable
    'https://repology.org/',
]

nitpicky = True

# -- Get version information and date from Git ----------------------------

try:
    from subprocess import check_output
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
except Exception:
    release = '<unknown>'
    today = '<unknown date>'

# -- Options for HTML output ----------------------------------------------

html_favicon = 'favicon.svg'
html_title = project + ' version ' + release

# -- Options for LaTeX output ---------------------------------------------

# See https://www.sphinx-doc.org/en/master/latex.html
latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
    'sphinxsetup': r"""
HeaderFamily=\rmfamily\bfseries,
div.note_border-TeXcolor={HTML}{E0E0E0},
div.note_border-width=0.5pt,
div.note_box-decoration-break=slice,
div.warning_border-TeXcolor={HTML}{E0E0E0},
div.warning_border-width=1.5pt,
div.warning_background-TeXcolor={HTML}{FBFBFB},
div.warning_box-decoration-break=slice,
div.topic_box-shadow=none,
div.topic_border-TeXcolor={HTML}{E0E0E0},
div.topic_border-width=0.5pt,
div.topic_box-decoration-break=slice,
""",
    'fontpkg': r"""
\usepackage{mathpazo}
\linespread{1.05}  % see http://www.tug.dk/FontCatalogue/urwpalladio/
\setmainfont{TeX Gyre Pagella}[Numbers=OldStyle]
\setmonofont{Latin Modern Mono Light}[Numbers=Lining]
""",
    'preamble': r"""
\urlstyle{tt}
""",
}

latex_engine = 'lualatex'
latex_use_xindy = False

latex_table_style = ['booktabs']

latex_documents = [
    (master_doc, 'nbsphinx.tex', project, author, 'howto'),
]

latex_show_urls = 'footnote'
latex_show_pagerefs = True

# -- Work-around to get LaTeX References at the same place as HTML --------

# See https://github.com/mcmtroffaes/sphinxcontrib-bibtex/issues/156

import sphinx.builders.latex.transforms

class DummyTransform(sphinx.builders.latex.transforms.BibliographyTransform):

    def run(self, **kwargs):
        pass

sphinx.builders.latex.transforms.BibliographyTransform = DummyTransform

# -- Options for EPUB output ----------------------------------------------

# These are just defined to avoid Sphinx warnings related to EPUB:
version = release
suppress_warnings = ['epub.unknown_project_files']

# -- Set default HTML theme (if none was given above) ---------------------

if 'html_theme' not in globals():
    try:
        import insipid_sphinx_theme
    except ImportError:
        pass
    else:
        html_theme = 'insipid'
        html_copy_source = False
        html_permalinks_icon = '#'

if globals().get('html_theme') == 'insipid':
    # This controls optional content in index.rst:
    tags.add('insipid')
