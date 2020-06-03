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

from tokens import ParenCite, TextCite, DocMetaData, DoubleQuote, MixedFraction, SimpleFraction, SpecialSection

AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCLEVELS=['part', 'chapter', 'section', 'subsection', 'subsubsection']
DOCOPTS='11pt,a4paper'
DOCTYPE='article'
H2_LEVEL='2'
PAREN_DATE_RE=re.compile(r'(.*) \((.*)\)')

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
                    '{preamble}'
                    '\\title{{{title}}}\n'
                    '\\author{{{author}}}\n'
                    '\\date{{{date}}}\n'
                    '\\begin{{document}}\n'
                    '\\maketitle\n'
                    '{inner}'
                    '{postamble}'
                    '\\end{{document}}\n')

        doctype, docopts = self.get_doctype_data()
        title, author, date = self.get_doc_metadata()

        return template.format(doctype=doctype,
                               docopts=docopts,
                               packages=self.render_packages(),
                               preamble=self.get_preamble(),
                               title=title,
                               author=author,
                               date=date,
                               inner=inner,
                               postamble=self.get_postamble())

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

    def get_preamble(self):
        bibpath = self.get_bib_path()
        if not bibpath:
            return ''
        return '\\addbibresource{"' + bibpath + '"}\n'

    def get_postamble(self):
        if not self.get_bib_path():
            return ''
        return '\\printbibliography\n'


class IdiomaticRenderer(CitationRenderer):
    def __init__(self, path):
        self.title = ''
        self.metadata = {}
        self.bib_printed = False
        self.quote_open = False
        super().__init__(path, DocMetaData, DoubleQuote, MixedFraction, SimpleFraction, SpecialSection)

    def render_heading(self, token):
        inner = self.render_inner(token)

        if inner.lower() == "frontmatter":
            return '\n\\thispagestyle{empty}\n\\frontmatter\n'

        if inner.lower() == "mainmatter":
            return '\n\\mainmatter\n'

        if inner.lower() == "backmatter":
            return '\n\\backmatter\n'

        if inner.lower() == "appendix" or inner.lower() == "appendices":
            return '\n\\appendix\n'

        if token.level == 1:
            self.title = self.title or inner
            return ''

        h2_level = int(self.metadata.get('H2Level', H2_LEVEL))
        level = token.level + h2_level - 2
        if level < 0:
            command = DOCLEVELS[0]
        elif level >= 0 and level < len(DOCLEVELS):
            command = DOCLEVELS[level]
        else:
            command = DOCLEVELS[-1]
        return '\n\\{command}{{{inner}}}\n'.format(command=command, inner=inner)

    @staticmethod
    def render_thematic_break(token):
        return '\\pagebreak\n'

    def render_doc_meta_data(self, token):
        self.metadata[token.key] = token.val
        return ''

    def render_double_quote(self, token):
        self.quote_open = not self.quote_open
        return '``' if self.quote_open else "''"

    @staticmethod
    def render_mixed_fraction(token):
        return '${z}\\frac{{{n}}}{{{d}}}$'.format(z=token.whole, n=token.numer, d=token.denom)

    @staticmethod
    def render_simple_fraction(token):
        return '$\\frac{{{n}}}{{{d}}}$'.format(n=token.numer, d=token.denom)

    def render_special_section(self, token):
        if token.content == 'BIBLIO':
            self.bib_printed = True
            return '\\printbibliography\n'
        if token.content == 'FIGURES':
            return '\\listoffigures\n'
        if token.content == 'TABLES':
            return '\\listoftables\n'
        if token.content == 'TOC':
            return '\\tableofcontents\n'

    def get_doctype_data(self):
        doctype, docopts = super().get_doctype_data()
        return (self.metadata.get('Doctype', doctype),
                self.metadata.get('Docopts', docopts))

    def get_doc_metadata(self):
        title, author, date = super().get_doc_metadata()
        return (self.title or title,
                self.metadata.get('Author', author),
                self.metadata.get('Date', date))

    def get_preamble(self):
        preamble = super().get_preamble()
        if 'SecNumDepth' in self.metadata:
            preamble += '\\setcounter{secnumdepth}{' + self.metadata['SecNumDepth'] + '}\n'
        if 'TocDepth' in self.metadata:
            preamble += '\\setcounter{tocdepth}{' + self.metadata['TocDepth'] + '}\n'
        return preamble

    def get_postamble(self):
        return '' if self.bib_printed else super().get_postamble()
