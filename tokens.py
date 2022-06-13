# mistletoe tokens for use in custom renderers.

import re
from mistletoe.span_token import SpanToken


class ParenCite(SpanToken):
    pattern = re.compile(r'\s\(([A-Z][A-Za-z]+[0-9]{4})\)')
    parse_inner = False


class TextCite(SpanToken):
    pattern = re.compile(r'\s([A-Z][A-Za-z]+[0-9]{4})')
    parse_inner = False


class DocMetaData(SpanToken):
    pattern = re.compile(
        r'\[(Author|Date|Doctype|Docopts|H2Level|MathPkg|SecNumDepth|TocDepth)\s*:\s*(.*)\]')
    parse_inner = False
    def __init__(self, match):
        self.key = match.group(1)
        self.val = match.group(2)


class DoubleQuote(SpanToken):
    pattern = re.compile(r'(")')
    parse_inner = False


class LatexLiteral(SpanToken):
    pattern = re.compile(r'\[\[([^\]]*)\]\]')
    parse_inner = False


class LatexPackageSimple(SpanToken):
    pattern = re.compile(r'\[Package\s*:\s*([^()\[\]]+)]')
    parse_inner = False


class LatexPackageWithOptions(SpanToken):
    pattern = re.compile(r'\[Package\s*:\s*([^\[\]]+)\(([^\[\]]+)\)]')
    parse_inner = False
    def __init__(self, match):
        self.pkg_name = match.group(1)
        self.pkg_opts = match.group(2)


class MixedFraction(SpanToken):
    pattern = re.compile(r'(\d+)\s([13])/([24])')
    parse_inner = False
    def __init__(self, match):
        self.whole = match.group(1)
        self.numer = match.group(2)
        self.denom = match.group(3)


class SimpleFraction(SpanToken):
    pattern = re.compile(r'(?<!\d\s)([13])/([24])')
    parse_inner = False
    def __init__(self, match):
        self.numer = match.group(1)
        self.denom = match.group(2)


class SimpleIndexItem(SpanToken):
    pattern = re.compile(r'!([A-Za-z]+)')
    parse_inner = False


class SpecialSection(SpanToken):
    pattern = re.compile(r'\[(BIBLIO|FIGURES|INDEX|TABLES|TOC)\]')
    parse_inner = False
