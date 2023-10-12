import logging
import os

import openai

from . import git

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = "gpt-4"


def setup_logging():
    DEBUG = os.environ.get("DEBUG", False)
    log_level = logging.DEBUG if __debug__ or DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER.debug("Debug mode enabled")


def commit_history():
    max_diff_length = 1000
    history = []
    for commit in git.latest_commits(5):
        if len(commit.diff) > max_diff_length:
            continue
        history.append({"role": "user", "content": commit.diff})
        history.append({"role": "assistant", "content": commit.message})

    return history


def generate_commit(input_diff: str) -> str:
    COMMIT_INSTRUCTION = """
You will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""

    system_message = {"role": "system", "content": COMMIT_INSTRUCTION}

    input_message = {"role": "user", "content": input_diff}

    history = []
    history.extend(commit_history())

    response = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[
            system_message,
            *history,
            input_message,
        ],
        temperature=0.2,
    )
    commit_msg = response.choices[0].message.content

    return commit_msg


def ci():
    setup_logging()
    input_diff = git.cached_diff()
    commit_msg = generate_commit(input_diff)
    git.create_commit(commit_msg)


if __name__ == "__main__":
    ci()
