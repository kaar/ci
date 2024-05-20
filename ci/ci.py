import os

import openai
from openai.types.chat import ChatCompletionMessageParam

from . import git

DRY_RUN = os.environ.get("TEST", False)

MODEL = "gpt-4o"
TEMPERATURE = 0.2
DEFAULT_MODEL = "gpt-4o"
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


def create_commit():
    input_diff = git.cached_diff()
    if not input_diff:
        raise ValueError("No changes to commit.")

    openai_client = openai.OpenAI()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": f"{COMMIT_INSTRUCTION}"},
        {"role": "user", "content": f"{input_diff.text}"},
    ]

    response = openai_client.chat.completions.create(
        messages=messages,
        model=MODEL,
        temperature=TEMPERATURE,
    )

    commit_msg = response.choices[0].message.content

    if DRY_RUN:
        return commit_msg if commit_msg else ""

    if not commit_msg:
        raise ValueError("Commit message cannot be empty.")

    git.create_commit(commit_msg)
