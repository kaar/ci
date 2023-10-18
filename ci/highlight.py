from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer

from . import markdown as md


def diff(text: str):
    return highlight(text, DiffLexer(), TerminalFormatter())


def markdown(text: str):
    return md.highlight(text)
