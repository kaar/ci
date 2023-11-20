from ci import git, highlight


def cached() -> None:
    diff = git.cached_diff()
    highlighed_diff = highlight.diff(diff.text)
    print(highlighed_diff)
