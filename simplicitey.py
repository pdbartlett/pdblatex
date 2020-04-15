import os
import os.path
import re
import subprocess
import sys

from datetime import datetime

import mistletoe
from mistletoe import Document
from mistletoe.latex_renderer import LaTeXRenderer
from mistletoe.span_token import SpanToken

# Constants for use in output document.
AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCOPTS='11pt,a4paper'
DOCTYPE='article'

def main(args):
    for filename in args:
        convert(filename)

def convert(filename):
    try:
        with CustomRenderer(filename) as renderer:
            with open(filename, 'r') as fin:
                rendered = renderer.render(Document(fin))
        outfile = newext(filename, '.tex')
        with open(outfile, 'w') as fout:
            fout.write(rendered)
        subprocess.run(['latexmk', '-pdf', outfile])
    except OSError as err:
        sys.exit('Problem processing "' + filename + '": ' + str(err))

def newext(filename, ext):
    if filename[-3:] == '.md':
        return filename[:-3] + ext
    return filename + ext


class ParenCite(SpanToken):
    pattern = re.compile(r" \(([A-Z][A-Za-z]+[0-9]{4})\)")
    def __init__(self, match_obj):
        self.citekey = match_obj.group(1)


class TextCite(SpanToken):
    pattern = re.compile(r" ([A-Z][A-Za-z]+[0-9]{4})")
    def __init__(self, match_obj):
        self.citekey = match_obj.group(1)


class CustomRenderer(LaTeXRenderer):
    def __init__(self, path):
        super().__init__(ParenCite, TextCite)
        self.path = path

    def render_paren_cite(self, token):
        template = ' \\parencite{{{citekey}}}'
        return template.format(citekey=token.citekey)

    def render_text_cite(self, token):
        template = ' \\textcite{{{citekey}}}'
        return template.format(citekey=token.citekey)

    def render_document(self, token):
        # From superclass; not sure it does much in current version.
        self.footnotes.update(token.footnotes)

        template = ('\\documentclass[{docopts}]{{{doctype}}}\n'
                    '{packages}'
                    '{setupbib}'
                    '\\title{{{title}}}\n'
                    '\\author{{{author}}}\n'
                    '\\date{{{date}}}\n'
                    '\\begin{{document}}\n'
                    '\\maketitle\n'
                    '{inner}'
                    '{printbib}'
                    '\\end{{document}}\n')

        basename = os.path.splitext(os.path.basename(self.path))[0]
        parts = basename.split('(')
        if len(parts) == 2:
            title = parts[0][:-1]
            date = parts[1][:-1]
        else:
            title = parts[0]
            date = datetime.today().strftime(DATE_FORMAT)

        title = title.replace('-', ' ').replace('_', ' ').title()

        bibpath = newext(self.path, '.bib')
        if os.path.isfile(bibpath):
            setupbib = ('\\usepackage[style=authoryear-ibid,backend=biber]{biblatex}\n'
                        '\\addbibresource{' + bibpath + '}\n')
            printbib = '\\printbibliography\n'
        else:
            setupbib = ''
            printbib = ''

        return template.format(doctype=DOCTYPE,
                               docopts=DOCOPTS,
                               packages=self.render_packages(),
                               setupbib=setupbib,
                               title=title,
                               author=AUTHOR,
                               date=date,
                               inner=self.render_inner(token),
                               printbib=printbib)


if __name__ == "__main__":
    main(sys.argv[1:])
