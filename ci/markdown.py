import textwrap

import pygments
from pygments.formatters import TerminalFormatter
from pygments.lexers.markup import MarkdownLexer


def wrap_text(text: str, width: int = 88, break_long_words: bool = False) -> str:
    lines = text.split("\n")
    wrapped_lines = [textwrap.fill(line, width=width, break_long_words=break_long_words) for line in lines]
    wrapped_text = "\n".join(wrapped_lines)
    return wrapped_text


def highlight(text: str) -> str:
    """Highlights the markdown syntax in the input text."""
    wrapped_text = wrap_text(text)
    return pygments.highlight(
        wrapped_text,
        MarkdownLexer(),
        TerminalFormatter(),
    )
