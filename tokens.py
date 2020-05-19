# mistletoe tokens for use in custom renderers.

import re
from mistletoe.span_token import SpanToken


__all__ = ['ParencCite', 'TextCite']


class ParenCite(SpanToken):
    pattern = re.compile(r" \(([A-Z][A-Za-z]+[0-9]{4})\)")
    parse_inner = False
    parse_group = 1


class TextCite(SpanToken):
    pattern = re.compile(r" ([A-Z][A-Za-z]+[0-9]{4})")
    parse_inner = False
    parse_group = 1
