import argparse
import logging
import os

from ci import commit, git, review

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = "gpt-4"


def setup_logging():
    DEBUG = os.environ.get("DEBUG", False)
    log_level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER.debug("Debug mode enabled")


def ci():
    """
    Options:
        --amend: Amend the last commit instead of creating a new one.
        --review <commit>: Review a commit, default is staged changes.
        - Read from stdin
    """
    setup_logging()
    argparser = argparse.ArgumentParser()

    argparser.add_argument("--amend", action="store_true")
    # Default value is "staged" and that will read the diff from git diff --cached
    argparser.add_argument("--review", nargs="?", const="staged")

    args = argparser.parse_args()

    match args.review:
        case None:
            pass
        case "staged":
            review.cached()
            return
        case "-":
            review.stdin()
            return
        case commit_hash if git.validate_commit_hash(commit_hash):
            review.commit(commit_hash)
            return
        case _:
            raise ValueError(f"Invalid review argument {args.review}")

    if args.amend:
        commit.amend()
    else:
        commit.new()


if __name__ == "__main__":
    ci()
