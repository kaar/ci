from ci import git, highlight


def cached() -> None:
    diff = git.cached_diff()
    highlighed_diff = highlight.diff(diff)
    print(highlighed_diff)
