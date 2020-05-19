import os
import os.path
import re
import subprocess
import sys

from datetime import datetime
from itertools import chain

import mistletoe
from mistletoe import Document
from mistletoe.latex_renderer import LaTeXRenderer

from tokens import ParenCite, TextCite, DocMetaData

AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCOPTS='11pt,a4paper'
DOCTYPE='article'
PAREN_DATE_RE = re.compile(r'(.*) \((.*)\)')

def render(filename, renderer):
    try:
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


class CitationRenderer(LaTeXRenderer):
    def __init__(self, path, *extras):
        self.path = path
        super().__init__(*chain([ParenCite, TextCite], extras))

    def render_paren_cite(self, token):
        return self.cite_helper('parencite', token)

    def render_text_cite(self, token):
        return self.cite_helper('textcite', token)

    def cite_helper(self, command, token):
        self.packages['biblatex'] = '[style=authoryear-ibid,backend=biber]'
        template = ' \\{command}{{{citekey}}}'
        return template.format(command=command, citekey=token.content)

    def render_document(self, token):
        # From superclass; not sure it does much in current version.
        self.footnotes.update(token.footnotes)

        # "Pre-render" inner content, so we can extract anything we need
        # in render_* methods rather than having to change core tokenisers.
        # Also allows render_* methods to register packages to add.
        inner = self.render_inner(token)

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

        doctype, docopts = self.get_doctype_data()
        title, author, date = self.get_doc_metadata()
        setupbib, printbib = self.get_bib_data()

        return template.format(doctype=doctype,
                               docopts=docopts,
                               packages=self.render_packages(),
                               setupbib=setupbib,
                               title=title,
                               author=author,
                               date=date,
                               inner=inner,
                               printbib=printbib)

    def get_doctype_data(self):
        return (DOCTYPE, DOCOPTS)

    def get_doc_metadata(self):
        basename = os.path.splitext(os.path.basename(self.path))[0]
        title = basename.replace('-', ' ').replace('_', ' ')
        match = PAREN_DATE_RE.match(title)
        if match:
            title = match.group(1)
            date = match.group(2)
        else:
            date = datetime.today().strftime(DATE_FORMAT)

        return (title.title(), AUTHOR, date)

    def get_bib_path(self):
        bibpath = newext(os.path.basename(self.path), '.bib')
        return bibpath if os.path.isfile(bibpath) else ''

    def get_bib_data(self):
        bibpath = self.get_bib_path()
        if not bibpath:
            return ('', '')

        setupbib = '\\addbibresource{"' + bibpath + '"}\n'
        printbib = '\\printbibliography\n'
        return (setupbib, printbib)


class IdiomaticRenderer(CitationRenderer):
    def __init__(self, path):
        self.title = ''
        self.metadata = {}
        self.has_appendix = False
        super().__init__(path, DocMetaData)

    def render_heading(self, token):
        inner = self.render_inner(token)
        if token.level == 1:
            if self.title:
                self.has_appendix = True
                if self.get_bib_path():
                    return '\n\\printbibliography\n\\appendix\n'
                return '\n\\appendix\n'
            else:
                self.title = inner
                return ''
        # TODO make levels doctype-dependent
        elif token.level == 2:
            level = 'section'
        elif token.level == 3:
            level = 'subsection'
        else:
            level = 'subsubsection'
        return '\n\\{level}{{{inner}}}\n'.format(level=level, inner=inner)

    def render_doc_meta_data(self, token):
        self.metadata[token.key] = token.val
        return ''

    def get_doctype_data(self):
        doctype, docopts = super().get_doctype_data()
        return (self.metadata.get('Doctype', doctype),
                self.metadata.get('Docopts', docopts))

    def get_doc_metadata(self):
        title, author, date = super().get_doc_metadata()
        return (self.title or title,
                self.metadata.get('Author', author),
                self.metadata.get('Date', date))

    def get_bib_data(self):
        setupbib, printbib = super().get_bib_data()
        return (setupbib, '' if self.has_appendix else printbib)
