# mistletoe tokens for use in custom renderers.

import re

from mistletoe.span_token import SpanToken

class ParenCite(SpanToken):
    pattern = re.compile(r" \(([A-Z][A-Za-z]+[0-9]{4})\)")
    def __init__(self, match_obj):
        self.citekey = match_obj.group(1)


class TextCite(SpanToken):
    pattern = re.compile(r" ([A-Z][A-Za-z]+[0-9]{4})")
    def __init__(self, match_obj):
        self.citekey = match_obj.group(1)
