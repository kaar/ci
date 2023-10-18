from ci import git, highlight


def show(commit_hash: str):
    text = git.show(commit_hash)
    highlighted_text = highlight.diff(text)
    print(highlighted_text)
