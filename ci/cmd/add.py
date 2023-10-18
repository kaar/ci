from typing import Optional

from ci import git


def add(file_path: Optional[str], patch: bool):
    """Add commit"""
    git.add(file_path, patch=patch)
