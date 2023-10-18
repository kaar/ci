from typing import Optional

from ci import git, highlight


def status(file_path: Optional[str]):
    """Show status"""

    text = git.status(file_path)
    highlighted_text = highlight.status(text)
    print(highlighted_text)
