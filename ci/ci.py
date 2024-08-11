"""
TODO: I don't trust the openai api. I should switch it out
"""

import logging
import os
from typing import Protocol
from pathlib import Path
import json


import openai
from openai.types.chat import ChatCompletionMessageParam

from . import git


def bool_env(key: str, default=False) -> bool:
    return os.environ.get(key, str(default)).lower() == "true"


DRY_RUN: bool = bool_env("TEST", False)
DEBUG: bool = bool_env("DEBUG", False)

# Adding example and history did not have much of an impact on the quality of the commit message
# I'm not sure why. I was hoping to get it to align better with how I write commit messages.
# I've tried both including it in the system context and as a user message.
# Maybe OpenAIs API is doing some cachine or something, because I don't see any changes at all to the output.
ADD_EXAMPLES: bool = bool_env("ADD_EXAMPLES", False)
ADD_HISTORY: bool = bool_env("ADD_HISTORY", False)
DATA_DIR = os.path.expanduser(f"{os.environ.get('XDG_DATA_DIR', '~/.local/share')}/ci")
CACHE_DIR = Path("/home/tibber/repos/kaar/ci/requests")
LOG_LEVEL = logging.INFO if DRY_RUN else logging.DEBUG if DEBUG else logging.WARN

logging.basicConfig(level=LOG_LEVEL, format="%(message)s")
LOGGER = logging.getLogger(__name__)

MODEL = "gpt-4o"
TEMPERATURE = 0.2
DEFAULT_MODEL = "gpt-4o"
COMMIT_INSTRUCTION = """
Act as a git commit message writer.

You will receive a git diff and respond with a git commit message that follows the guidelines below:
Limit the subject line to 50 characters.
Capitalize the subject line.
Do not end the subject line with a period.
Use the imperative mood in the subject line.
Separate subject from body with a blank line.
Wrap the body at 72 characters.
Use code examples if needed to descripe the intent of the commit.
Use short and concise sentences, shorter is better.

### Additional Notes:
* You should also look for any obvious bugs in the code, summarize them at the end if you find any.
"""


class Cache(Protocol):
    def set(self, key: str, value: dict): ...

    def get(self, key: str) -> dict: ...

    def exists(self, key: str) -> bool: ...

    def clear(self): ...


class JsonFileCache(Cache):
    def __init__(self, cache_dir: Path = Path(".cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        path = self.cache_dir / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def set(self, key, value: dict):
        with open(self._path(key), "w") as f:
            LOGGER.debug(f"Writing cache for {key}")
            json.dump(value, f)

    def get(self, key) -> dict:
        with open(self._path(key), "r") as f:
            LOGGER.debug(f"Reading cache for {key}")
            return json.load(f)

    def exists(self, key):
        LOGGER.debug(f"Checking cache for {key}")
        return (self._path(key)).exists()

    def clear(self):
        for file in self.cache_dir.rglob("*.json"):
            LOGGER.debug(f"Removing cache file {file}")
            file.unlink()


def load_example():
    diff = open(f"{DATA_DIR}/example_1.diff").read()
    msg = open(f"{DATA_DIR}/example_1.msg").read()
    return {
        "diff": diff,
        "msg": msg,
    }


def create_example_context(example):
    return f"Example:\n```diff\n{example['diff']}\n```\n```plaintext\n{example['msg']}\n```"


def create_messages() -> list[ChatCompletionMessageParam]:
    messages: list[ChatCompletionMessageParam] = []
    LOGGER.info(COMMIT_INSTRUCTION)
    messages.append({"role": "system", "content": f"{COMMIT_INSTRUCTION}"})

    system_message = COMMIT_INSTRUCTION

    if ADD_EXAMPLES:
        example = load_example()
        messages.append({"role": "user", "content": f"{example['diff']}"})
        messages.append({"role": "assistant", "content": f"{example['diff']}"})
        # example_context = f"\n### Examples\n```diff\n{example['diff']}\n```\n```plaintext\n{example['msg']}\n```"
        # LOGGER.info(example_context)
        # system_message += example_context
        # messages.append({"role": "user", "content": f"{example_context}"})

    if ADD_HISTORY:
        n = 3
        log_history = git.log(n)
        log_context = f"\n### Last {n} commits:\n```plaintext\n{log_history}\n```\n"
        # LOGGER.info(log_context)
        system_message += log_context
        # messages.append({"role": "user", "content": f"{log_context}"})

    input_diff = git.cached_diff()
    if not input_diff:
        raise ValueError("No changes to commit.")
    messages.append({"role": "user", "content": f"{input_diff.text}"})

    return messages


def create_commit():
    print("Creating commit message...")
    try:
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
        print(commit_msg)

        if DRY_RUN:
            return commit_msg if commit_msg else ""

        if not commit_msg:
            raise ValueError("Commit message cannot be empty.")

        git.create_commit(commit_msg)
    except Exception as e:
        print(f"Error: {e}")
        raise e
