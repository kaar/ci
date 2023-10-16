import logging
import os

from ci import git, models, openai

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = "gpt-4"


def setup_logging():
    DEBUG = os.environ.get("DEBUG", False)
    log_level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER.debug("Debug mode enabled")


def commit_history():
    max_diff_length = 2500
    history = []
    for commit in git.latest_commits(5):
        if len(commit.diff) > max_diff_length:
            LOGGER.debug(f"Skipping commit with diff length {len(commit.diff)}")
            continue
        history.append(models.UserMessage(commit.diff))
        history.append(models.AssistantMessage(commit.message))

    return history


def generate_commit(input_diff: str) -> str:
    COMMIT_INSTRUCTION = """
You will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""

    system_message = models.SystemMessage(COMMIT_INSTRUCTION)
    history = []
    input_message = models.UserMessage(input_diff)

    response = openai.chat_completion(
        request=models.ChatRequest(
            model=DEFAULT_MODEL,
            messages=[
                system_message,
                *history,
                input_message,
            ],
            temperature=0.2,
        )
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
