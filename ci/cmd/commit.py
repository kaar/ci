import openai

from ci import git

DEFAULT_MODEL = "gpt-4o"


def create_new_commit(history=0):
    """
    Create a new Git commit.

    Args:
        history (int): Number of latest commits to consider for generating commit message.

    Raises:
        ValueError: If the input diff is empty or git commands fail.
    """
    input_diff = git.cached_diff()
    if not input_diff:
        raise ValueError("No changes to commit.")

    commit_history = git.latest_commits(history) if history else []
    commit_msg = _ask_for_commit_msg(input_diff.text, commit_history=commit_history)
    if not commit_msg:
        raise ValueError("Commit message cannot be empty.")

    git.create_commit(commit_msg)


def amend_commit():
    """
    Amend the latest Git commit.

    Args:
        history (int): Number of latest commits to consider for generating commit message.

    Raises:
        ValueError: If the input diff is empty or git commands fail.
    """
    input_diff = git.cached_diff()
    if not input_diff:
        raise ValueError("No changes to commit.")

    commit_history = git.latest_commits(1)

    commit_msg = _ask_for_commit_msg(input_diff.text, commit_history=commit_history)

    git.amend_commit(commit_msg)


def _ask_for_commit_msg(
    input_diff: str,
    commit_history: list,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
    """This function takes a git diff as input and returns a git commit message"""

    COMMIT_INSTRUCTION = """
You will receive a git diff and respond with a git commit message.
Provide a clear and concise commit message based on the changes in the diff.
Try to describe what the change is intended to accomplish.

### Guidelines:
Limit the subject line to 50 characters.
Capitalize the subject line.
Do not end the subject line with a period.
Use the imperative mood in the subject line.
Separate subject from body with a blank line.
Wrap the body at 72 characters.
Prefer descriptive sentences over bulletpoints.
Avoid using words like refactor, update, fix, or change.
"""
    # history = history or []

    openai_client = openai.OpenAI()

    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": COMMIT_INSTRUCTION,
            },
            {
                "role": "user",
                "content": input_diff,
            },
        ],
        model=model,
        temperature=temperature,
    )

    commit_msg = response.choices[0].message.content

    return commit_msg if commit_msg else ""
