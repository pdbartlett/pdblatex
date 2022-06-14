# pdblatex
Utilities for working with LaTeX, currently focussed on generating from Markdown.

## Sophistory

1. Ensure you have a "relative up-to-date" version of Python3:

   ```sh
   $ python3 -V
   Python 3.8.9
   ```
   
1. Ensure you have a valid LaTeX installation, complete with `latexmk`:

   ```sh
   $ which latexmk
   /Library/TeX/texbin/latexmk
   ```

1. Install `mistletoe`, the super-useful library upon which `sophistory` depends:

   ```sh
   $ pip3 install mistletoe
   ```

1. Write your markdown doc, using the supplied examples for insipration.
1. Generate `.pdf` file output, which `sophistory` does via a LaTeX intermediate:

   ```sh
   $ python3 sophistory.py your-doc.md
   ```

1. DONE!
