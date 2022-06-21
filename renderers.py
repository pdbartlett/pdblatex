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

from enums import DocMetaDataType, GeneratedContentType, SpecialSectionType
from tokens import (ParenCite, TextCite, DocMetaData, DoubleQuote,
                    GeneratedContent, LatexLiteral, LatexPackageSimple,
                    LatexPackageWithOptions, MixedFraction, SimpleFraction,
                    SimpleIndexItem)

AUTHOR='Sophie Bartlett'
DATE_FORMAT='%d %B %Y'
DOCLEVELS=['part', 'chapter', 'section', 'subsection', 'subsubsection']
DOCOPTS='11pt,a4paper'
DOCTYPE='article'
H2_LEVEL='2'
MATHPKG='amsmath'

BIBLATEX_OPTS = '[style=authoryear-ibid,backend=biber]'
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
        self.abstract = ''
        self.para_is_abstract = False
        self.preamble = STD_PREAMBLE
        self.biblios = []
        self.metadata = {}
        self.quote_open = False
        super().__init__(*chain([ParenCite, TextCite, DocMetaData, DoubleQuote,
                                 GeneratedContent, LatexLiteral,
                                 LatexPackageSimple, LatexPackageWithOptions,
                                 MixedFraction, SimpleFraction,
                                 SimpleIndexItem],
                                extras))

    def render_file(self):
        try:
            with open(self.path, 'r') as fin:
                rendered = self.render(Document(fin))
            outfile = self.newext('.tex')
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
                    '{abstract}'
                    '{inner}'
                    '\\end{{document}}\n')

        title, author, date, doctype, docopts = self.get_doc_metadata()
        preamble = self.get_preamble()
        # Do this last in case other calls add more.
        packages = self.render_packages()

        return template.format(doctype=doctype,
                               docopts=docopts,
                               title=title,
                               author=author,
                               date=date,
                               packages=packages,
                               preamble=preamble,
                               abstract=self.abstract,
                               inner=inner)

    def render_packages(self):
        self.packages['fancyhdr'] = '' # Used in STD_PREAMBLE.
        mathpkg = self.metadata.get(DocMetaDataType.MathPkg, MATHPKG)
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
        self.packages.setdefault('biblatex', BIBLATEX_OPTS)

    def render_paragraph(self, token):
        default = super().render_paragraph(token)
        if self.para_is_abstract:
            self.abstract += default
            return ''

        return default

    def render_heading(self, token):
        inner = self.render_inner(token)

        if inner.upper() == SpecialSectionType.ABSTRACT.name:
            self.para_is_abstract = True
            self.abstract = '\\begin{abstract}\n'
            return ''

        if self.para_is_abstract:
            self.para_is_abstract = False
            self.abstract += '\\end{abstract}\n'

        if inner.upper() == SpecialSectionType.FRONTMATTER.name:
            return '\n\\thispagestyle{empty}\n\\frontmatter\n'

        if inner.upper() == SpecialSectionType.MAINMATTER.name:
            return '\n\\mainmatter\n'

        if inner.upper() == SpecialSectionType.BACKMATTER.name:
            return '\n\\backmatter\n'

        if inner.upper() in [SpecialSectionType.APPENDIX.name,
                             SpecialSectionType.APPENDICES.name]:
            return '\n\\appendix\n'

        if token.level == 1:
            if self.title:
                self.logger.warning(
                    "Multiple top-level headings; ignoring all but first")
            else:
                self.title = inner
            return ''

        h2_level = int(self.metadata.get(DocMetaDataType.H2Level, H2_LEVEL))
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
        self.metadata[DocMetaDataType[token.key]] = token.val
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
            path = self.newext('.tmp{}.bib'.format(len(self.biblios)))
            self.biblios.append(path)
            self.preamble += '\\begin{{filecontents*}}{{{}}}\n'.format(path)
            self.preamble += self.render_raw_text(token.children[0], False)
            self.preamble += '\\end{filecontents*}\n'
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

    def render_simple_index_item(self, token):
        self.packages['makeidx'] = ''
        return '{i}\\index{{{i}}}'.format(i=token.content)

    @staticmethod
    def render_simple_fraction(token):
        return '$\\frac{{{n}}}{{{d}}}$'.format(n=token.numer, d=token.denom)

    def render_generated_content(self, token):
        if token.content == GeneratedContentType.BIBLIO.name:
            self.add_biblatex()
            return '\\printbibliography\n'
        if token.content == GeneratedContentType.FIGURES.name:
            return '\\listoffigures\n'
        if token.content == GeneratedContentType.INDEX.name:
            self.packages['makeidx'] = ''
            self.preamble += '\\makeindex\n'
            return '\\printindex\n'
        if token.content == GeneratedContentType.TABLES.name:
            return '\\listoftables\n'
        if token.content == GeneratedContentType.TOC.name:
            return '\\tableofcontents\n'

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
                self.metadata.get(DocMetaDataType.Author, AUTHOR),
                self.metadata.get(DocMetaDataType.Date, date),
                self.metadata.get(DocMetaDataType.DocType, DOCTYPE),
                self.metadata.get(DocMetaDataType.DocOpts, DOCOPTS))

    def get_preamble(self):
        preamble = self.preamble
        if 'SecNumDepth' in self.metadata:
            preamble += ('\\setcounter{secnumdepth}{' +
                self.metadata[DocMetaDataType.SecNumDepth] + '}\n')
        if 'TocDepth' in self.metadata:
            preamble += ('\\setcounter{tocdepth}{' +
                self.metadata[DocMetaDataType.TocDepth] + '}\n')
        bibpath = self.newext('.bib')
        if os.path.isfile(bibpath):
            self.biblios.append(os.path.basename(bibpath))
        for biblio in self.biblios:
            preamble += '\\addbibresource{{{}}}\n'.format(biblio)
        return preamble

    def newext(self, ext):
        if self.path[-3:] == '.md':
            return self.path[:-3] + ext
        return self.path + ext
