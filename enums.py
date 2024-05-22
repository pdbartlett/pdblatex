# enumerated types for used in tokenisers/renderers

from enum import Enum


class DocMetaDataType(Enum):
    Author, Date, ColorTheme, DocType, DocOpts, H2Level, MathPkg, SecNumDepth, Theme, TocDepth = range(10)


class GeneratedContentType(Enum):
    BIBLIO, FIGURES, INDEX, TABLES, TOC = range(5)


class SpecialSectionType(Enum):
    ABSTRACT, FRONTMATTER, MAINMATTER, BACKMATTER, APPENDIX, APPENDICES = range(6)


class SpecialSectionPrefixType(Enum):
    FIGURE, TABLE = range(2)
