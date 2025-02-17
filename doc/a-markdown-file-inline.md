# Using Markdown Files

Sphinx on its own doesn't know how to handle Markdown files,
but there are extensions that enable their usage as Sphinx source files.
For an example, see the
[Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/markdown.html).

Alternatively, when using `nbsphinx` it is also possible to use Markdown
files via [custom notebook formats](custom-formats.pct.py).

You only need to install the [jupytext](https://jupytext.readthedocs.io/)
package and add a configuration setting to `conf.py`,
which can be used to select one of
[several Markdown flavors supported by jupytext](https://jupytext.readthedocs.io/en/latest/formats-markdown.html)
(here we are using R Markdown):

```python
nbsphinx_custom_formats = {
    '.md': ['jupytext.reads', {'fmt': 'Rmd'}],
}
```

This very page was generated from a Markdown file using these settings.


## Links to Notebooks (and Other Sphinx Source Files)

Links to other Sphinx source files can be created like in
[Markdown cells of notebooks](markdown-cells.ipynb#Links-to-Other-Notebooks).


## Math

Mathematical equations can be used just like in
[Markdown cells of notebooks](markdown-cells.ipynb#Equations).

Inline like this: $\text{e}^{i\pi} = -1$.


## Tables

A     | B     | A and B
------|-------|--------
False | False | False
True  | False | False
False | True  | False
True  | True  | True


## Images

![Jupyter notebook icon](images/notebook_icon.png)
