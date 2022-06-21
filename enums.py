# enumerated types for used in tokenisers/renderers

from enum import Enum


class DocMetaDataType(Enum):
    Author, Date, DocType, DocOpts, H2Level, MathPkg, SecNumDepth, TocDepth = range(8)


class GeneratedContentType(Enum):
    BIBLIO, FIGURES, INDEX, TABLES, TOC = range(5)


class SpecialSectionType(Enum):
    ABSTRACT, FRONTMATTER, MAINMATTER, BACKMATTER, APPENDIX, APPENDICES = range(6)
