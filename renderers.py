import os
import os.path
import re

from datetime import datetime

from mistletoe.latex_renderer import LaTeXRenderer

from tokens import ParenCite, TextCite

# Constants for use in output document.
AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCOPTS='11pt,a4paper'
DOCTYPE='article'
PAREN_DATE_RE = re.compile(r'(.*) \((.*)\)')

def newext(filename, ext):
    if filename[-3:] == '.md':
        return filename[:-3] + ext
    return filename + ext


class CitationRenderer(LaTeXRenderer):
    def __init__(self, path):
        super().__init__(ParenCite, TextCite)
        self.path = path

    @staticmethod
    def render_paren_cite(token):
        template = ' \\parencite{{{citekey}}}'
        return template.format(citekey=token.content)

    @staticmethod
    def render_text_cite(token):
        template = ' \\textcite{{{citekey}}}'
        return template.format(citekey=token.content)

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
        title = basename.replace('-', ' ').replace('_', ' ')
        match = PAREN_DATE_RE.match(title)
        if match:
            title = match.group(1)
            date = match.group(2)
        else:
            date = datetime.today().strftime(DATE_FORMAT)

        bibpath = newext(os.path.basename(self.path), '.bib')
        if os.path.isfile(bibpath):
            setupbib = ('\\usepackage[style=authoryear-ibid,backend=biber]{biblatex}\n'
                        '\\addbibresource{"' + bibpath + '"}\n')
            printbib = '\\printbibliography\n'
        else:
            setupbib = ''
            printbib = ''

        return template.format(doctype=DOCTYPE,
                               docopts=DOCOPTS,
                               packages=self.render_packages(),
                               setupbib=setupbib,
                               title=title.title(),
                               author=AUTHOR,
                               date=date,
                               inner=self.render_inner(token),
                               printbib=printbib)
