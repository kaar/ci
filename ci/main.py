import sys

import openai

from . import git

DEFAULT_MODEL = "gpt-3.5-turbo"


def ci():
    input_diff = git.cached_diff()
    # input_diff = sys.stdin.read()

    COMMIT_INSTRUCTION = """
You are going to receive a git diff and you are going to provide a git commit with the format: {Subject}\n\n{Message}.
Subject is a short description of the change.
For subject use imperative mood.
Subject line is not allowed to be longer than 50 characters.
Message is a more detailed description of the code change.
Message is not needed for trivial changes.
Be direct, try to eliminate filler words and phrases in these sentences.
Shorter is always better.
"""
    system_message = {"role": "system", "content": COMMIT_INSTRUCTION}

    # Don't include diffs that are too long
    max_diff_length = 1000

    history = []
    for commit in git.latest_commits(5):
        if len(commit.diff) > max_diff_length:
            continue
        history.append({"role": "user", "content": commit.diff})
        history.append({"role": "assistant", "content": commit.message})

    input_message = {"role": "user", "content": input_diff}

    response = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[
            system_message,
            *history,
            input_message,
        ],
        temperature=0,
    )

    print(response)

    commit_msg = response.choices[0].message.content
    print(commit_msg)
    git.create_commit(commit_msg)


if __name__ == "__main__":
    ci()
