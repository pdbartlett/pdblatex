import os
import os.path
import re
import subprocess
import sys

from datetime import datetime

import mistletoe
from mistletoe import Document

from renderers import CitationRenderer, newext

def main(args):
    for filename in args:
        convert(filename)

def convert(filename):
    try:
        with CitationRenderer(filename) as renderer:
            with open(filename, 'r') as fin:
                rendered = renderer.render(Document(fin))
        outfile = newext(filename, '.tex')
        with open(outfile, 'w') as fout:
            fout.write(rendered)
        subprocess.run(['latexmk', '-pdf', outfile])
    except OSError as err:
        sys.exit('Problem processing "' + filename + '": ' + str(err))

if __name__ == "__main__":
    main(sys.argv[1:])
