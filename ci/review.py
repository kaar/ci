import sys

from ci import git, llm, markdown


def print_review(code_review: str):
    highlighted_code_review = markdown.highlight(code_review)
    print(highlighted_code_review)


def cached() -> None:
    diff = git.cached_diff()
    code_review = llm.review(diff)
    print_review(code_review)


def commit(commit_hash: str) -> None:
    diff = git.show(commit_hash)
    code_review = llm.review(diff)
    print_review(code_review)


def stdin() -> None:
    diff = sys.stdin.read()
    code_review = llm.review(diff)
    print_review(code_review)
