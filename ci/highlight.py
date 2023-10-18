import textwrap

import pygments
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer
from pygments.lexers.markup import MarkdownLexer


def diff(text: str) -> str:
    """
    Highlights the diff syntax in the input text.

    Args:
        text: The text to highlight.

    Returns:
        The highlighted text.
    """
    return pygments.highlight(text, DiffLexer(), TerminalFormatter())


def wrap_text(text: str, width: int = 88, break_long_words: bool = False) -> str:
    """
    Wraps the input text to the specified width.

    Args:
        text: The text to wrap.
        width: The width to wrap to.
        break_long_words: If true, long words will be broken.

    Returns:
        The wrapped text.
    """
    lines = text.split("\n")
    wrapped_lines = [textwrap.fill(line, width=width, break_long_words=break_long_words) for line in lines]
    wrapped_text = "\n".join(wrapped_lines)
    return wrapped_text


def markdown(text: str, wrap: bool = True):
    """
    Highlights the markdown syntax in the input text.

    Args:
        text: The text to highlight.
        wrap: If true, the text will be wrapped to 88 characters.

    Returns:
        The highlighted text.
    """
    if wrap:
        text = wrap_text(text)

    return pygments.highlight(text, MarkdownLexer(), TerminalFormatter())


def status(status_text: str):
    """
    Highlights the git status output.

    Args:
        status_text: The text to highlight.

    Returns:
        The highlighted text.
    """
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    STATUS_COLORS = {
        "On branch": BLUE,
        "Changes to be committed:": GREEN,
        "Changes not staged for commit:": YELLOW,
        "Untracked files:": RED,
        "modified:": PURPLE,
        "new file:": PURPLE,
    }

    lines = status_text.split('\n')
    highlighted = []

    for line in lines:
        for status, color in STATUS_COLORS.items():
            if status in line:
                highlighted.append(f'{color}{line}{RESET}')
                break
        else:
            highlighted.append(line)

    return '\n'.join(highlighted)
