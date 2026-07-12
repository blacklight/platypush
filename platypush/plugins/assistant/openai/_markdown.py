import re

_CODE_FENCE = re.compile(r'^[ \t]*```[^\n]*\n?', re.MULTILINE)
_INLINE_CODE = re.compile(r'`([^`\n]*)`')
_IMAGE = re.compile(r'!\[([^\]]*)\]\([^)]*\)')
_LINK = re.compile(r'\[([^\]]+)\]\([^)]*\)')
_BOLD_ITALIC_ASTERISK = re.compile(r'(\*{1,3})(?!\s)([^*\n]+?)(?<!\s)\1')
_BOLD_ITALIC_UNDERSCORE = re.compile(
    r'(?<![\w\\])(_{1,3})(?!\s)([^_\n]+?)(?<!\s)\1(?!\w)'
)
_STRIKETHROUGH = re.compile(r'~~([^~\n]+)~~')
_HEADER = re.compile(r'^[ \t]{0,3}#{1,6}[ \t]+', re.MULTILINE)
_BLOCKQUOTE = re.compile(r'^[ \t]{0,3}>[ \t]?', re.MULTILINE)
_HORIZONTAL_RULE = re.compile(r'^[ \t]{0,3}(?:-{3,}|\*{3,}|_{3,})[ \t]*$', re.MULTILINE)
_LIST_BULLET = re.compile(r'^([ \t]*)[-*+][ \t]+', re.MULTILINE)
_TABLE_SEPARATOR = re.compile(
    r'^[ \t]*\|?[ \t]*:?-{2,}:?[ \t]*(?:\|[ \t]*:?-{2,}:?[ \t]*)+\|?[ \t]*$',
    re.MULTILINE,
)
_TABLE_PIPES = re.compile(r'^[ \t]*\|(.*)\|[ \t]*$', re.MULTILINE)
_BLANK_LINES = re.compile(r'\n{3,}')


def strip_markdown(text: str) -> str:
    """
    Strip the most common Markdown formatting elements from a text, so that it
    can be cleanly rendered by a text-to-speech engine.

    :param text: The (possibly Markdown-formatted) input text.
    :return: The text with Markdown formatting elements removed.
    """
    if not text:
        return text

    text = _CODE_FENCE.sub('', text)
    text = _INLINE_CODE.sub(r'\1', text)
    text = _IMAGE.sub(r'\1', text)
    text = _LINK.sub(r'\1', text)
    text = _BOLD_ITALIC_ASTERISK.sub(r'\2', text)
    text = _BOLD_ITALIC_UNDERSCORE.sub(r'\2', text)
    text = _STRIKETHROUGH.sub(r'\1', text)
    text = _HEADER.sub('', text)
    text = _BLOCKQUOTE.sub('', text)
    text = _HORIZONTAL_RULE.sub('', text)
    text = _LIST_BULLET.sub(r'\1', text)
    text = _TABLE_SEPARATOR.sub('', text)
    text = _TABLE_PIPES.sub(lambda m: m.group(1).replace('|', ', '), text)
    text = _BLANK_LINES.sub('\n\n', text)
    return text.strip()
