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
    pattern = re.compile(r'(Author|Date|Doctype|Docopts)\s*:\s*\[(.*)\]')
    parse_inner = False
    def __init__(self, match):
        self.key = match.group(1)
        self.val = match.group(2)
