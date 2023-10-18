import sys

from ci import git, llm


def print_review(review_args):
    """
    LLM will review a git diff and provide a code review.
    """
    match review_args:
        case "staged":
            diff = git.cached_diff()
            code_review = llm.review(diff)
        case "-":
            diff = sys.stdin.read()
            code_review = llm.review(diff)
        case commit_hash if git.validate_commit_hash(commit_hash):
            diff = git.show(commit_hash)
            code_review = llm.review(diff)
        case _:
            raise ValueError(f"Invalid review argument {review_args}")

    print(code_review)
