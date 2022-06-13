import logging
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

from tokens import (ParenCite, TextCite, DocMetaData, DoubleQuote, LatexLiteral,
                    LatexPackageSimple, LatexPackageWithOptions, MixedFraction,
                    SimpleFraction, SpecialSection)

AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCLEVELS=['part', 'chapter', 'section', 'subsection', 'subsubsection']
DOCOPTS='11pt,a4paper'
DOCTYPE='article'
H2_LEVEL='2'
MATHPKG='amsmath'
PAREN_DATE_RE=re.compile(r'(.*) \((.*)\)')
STD_PREAMBLE='''
% Make title and author available
\\makeatletter
\\let\\inserttitle\@title
\\let\\insertauthor\@author
\\makeatother
% Put title and author in header
\\pagestyle{fancy}
\\fancyhf{}
\\lhead{``\\inserttitle''}
\\rhead{\\insertauthor}
\\cfoot{\\thepage}
\\addtolength{\\headheight}{2pt} % space for the rule
'''


class IdiomaticRenderer(LaTeXRenderer):
    def __init__(self, path, *extras):
        self.path = path
        self.logger = logging.getLogger(__name__)
        self.title = ''
        self.preamble = STD_PREAMBLE
        self.metadata = {}
        self.quote_open = False
        super().__init__(*chain([ParenCite, TextCite, DocMetaData, DoubleQuote,
                                 LatexLiteral, LatexPackageSimple,
                                 LatexPackageWithOptions, MixedFraction,
                                 SimpleFraction, SpecialSection], extras))

    def render_file(self):
        try:
            with open(self.path, 'r') as fin:
                rendered = self.render(Document(fin))
            outfile = self.newext(self.path, '.tex')
            with open(outfile, 'w') as fout:
                fout.write(rendered)
            subprocess.run(['latexmk', '-pdf', outfile])
        except OSError as err:
            sys.exit('Problem processing "' + self.path + '": ' + str(err))

    def render_document(self, token):
        # From superclass; not sure it does much in current version.
        self.footnotes.update(token.footnotes)

        # "Pre-render" inner content, so we can extract anything we need
        # in render_* methods rather than having to change core tokenisers.
        # Also allows render_* methods to register packages to add.
        inner = self.render_inner(token)

        template = ('\\documentclass[{docopts}]{{{doctype}}}\n'
                    '\\title{{{title}}}\n'
                    '\\author{{{author}}}\n'
                    '\\date{{{date}}}\n'
                    '{packages}'
                    '{preamble}'
                    '\\begin{{document}}\n'
                    '\\maketitle\n'
                    '{inner}'
                    '\\end{{document}}\n')

        doctype, docopts = self.get_doctype_data()
        title, author, date = self.get_doc_metadata()

        return template.format(doctype=doctype,
                               docopts=docopts,
                               title=title,
                               author=author,
                               date=date,
                               packages=self.render_packages(),
                               preamble=self.get_preamble(),
                               inner=inner)

    def render_packages(self):
        self.packages['fancyhdr'] = '' # Used in STD_PREAMBLE.
        mathpkg = self.metadata.get('MathPkg', MATHPKG)
        if mathpkg.lower() != 'none':
            self.packages[mathpkg] = ''
        return super().render_packages()

    def render_paren_cite(self, token):
        return self.cite_helper('parencite', token)

    def render_text_cite(self, token):
        return self.cite_helper('textcite', token)

    def cite_helper(self, command, token):
        self.add_biblatex()
        template = ' \\{command}{{{citekey}}}'
        return template.format(command=command, citekey=token.content)

    def add_biblatex(self):
        self.packages['biblatex'] = '[style=authoryear-ibid,backend=biber]'

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
            if self.title:
                self.logger.warning(
                    "Multiple top-level headings; ignoring all but first")
            else:
                self.title = inner
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
    def render_latex_literal(token):
        return token.content

    def render_latex_package_simple(self, token):
        self.packages[token.content] = ''
        return ''

    def render_latex_package_with_options(self, token):
        self.packages[token.pkg_name] = '[' + token.pkg_opts + ']'
        return ''

    def render_block_code(self, token):
        if token.language.lower() == 'bibtex':
            self.add_biblatex()
            path = self.newext(os.path.basename(self.path), '.tmp.bib')
            self.preamble += '\\begin{{filecontents*}}{{{}}}\n'.format(path)
            self.preamble += self.render_raw_text(token.children[0], False)
            self.preamble += '\\end{filecontents*}\n'
            self.preamble += '\\addbibresource{{{}}}\n'.format(path)
            return ''
        if token.language.lower() == 'inlinelatex':
            return self.render_raw_text(token.children[0], False)
        if token.language.lower() == 'preamblelatex':
            self.preamble += self.render_raw_text(token.children[0], False)
            return ''
        return super().render_block_code(token)

    @staticmethod
    def render_mixed_fraction(token):
        return '${z}\\frac{{{n}}}{{{d}}}$'.format(z=token.whole,
                                                  n=token.numer, d=token.denom)

    @staticmethod
    def render_simple_fraction(token):
        return '$\\frac{{{n}}}{{{d}}}$'.format(n=token.numer, d=token.denom)

    def render_special_section(self, token):
        if token.content == 'BIBLIO':
            self.add_biblatex()
            return '\\addcontentsline{toc}{section}{\\bibname}\n\\printbibliography\n'
        if token.content == 'FIGURES':
            return '\\listoffigures\n'
        if token.content == 'INDEX':
            self.packages['makeidx'] = ''
            self.preamble += '\\makeindex\n'
            return '\\printindex\n'
        if token.content == 'TABLES':
            return '\\listoftables\n'
        if token.content == 'TOC':
            self.packages['tocbibind'] = '[section,nottoc,notbib]'
            return '\\tableofcontents\n'

    def get_doctype_data(self):
        return (self.metadata.get('Doctype', DOCTYPE),
                self.metadata.get('Docopts', DOCOPTS))

    def get_doc_metadata(self):
        basename = os.path.splitext(os.path.basename(self.path))[0]
        title = basename.replace('_', ' ')
        match = PAREN_DATE_RE.match(title)
        if match:
            title = match.group(1)
            date = match.group(2)
        else:
            date = datetime.today().strftime(DATE_FORMAT)

        return (self.title or title,
                self.metadata.get('Author', AUTHOR),
                self.metadata.get('Date', date))

    def get_preamble(self):
        preamble = self.preamble
        if 'SecNumDepth' in self.metadata:
            preamble += '\\setcounter{secnumdepth}{' + self.metadata['SecNumDepth'] + '}\n'
        if 'TocDepth' in self.metadata:
            preamble += '\\setcounter{tocdepth}{' + self.metadata['TocDepth'] + '}\n'
        return preamble

    @staticmethod
    def newext(filename, ext):
        if filename[-3:] == '.md':
            return filename[:-3] + ext
        return filename + ext
