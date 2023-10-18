import argparse
import logging
import os

from ci import commit, git, models, openai, review

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


def amend_commit():
    COMMIT_INSTRUCTION = """
You will receive first receive the previous commit message.
Then you will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""
    last_commit = git.last_commit()
    input_diff = git.cached_diff()

    messages = [
        models.SystemMessage(COMMIT_INSTRUCTION),
        models.UserMessage(last_commit.message),
        models.UserMessage(input_diff),
    ]
    response = openai.chat_completion(
        request=models.ChatRequest(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.2,
        )
    )
    commit_msg = response.choices[0].message.content
    git.amend_commit(commit_msg)


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

    if args.review:
        LOGGER.debug(f"Reviewing {args.review}")
        review.print_review(args.review)
        return

    if args.amend:
        amend_commit()
    else:
        commit.new()


if __name__ == "__main__":
    ci()
