from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer

from . import markdown as md


def diff(text: str):
    return highlight(text, DiffLexer(), TerminalFormatter())


def markdown(text: str):
    return md.highlight(text)


def status(status_text: str):
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
