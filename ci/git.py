import re
import subprocess
from dataclasses import dataclass


def cached_diff() -> str:
    diff = subprocess.check_output(["git", "diff", "--cached"])
    return diff.decode("utf-8")


def create_commit(message: str) -> None:
    """
    Creates a commit with the given message.

    Set editor by setting the EDITOR environment variable.

    Args:
        message: The commit message.

    Returns:
        None
    """
    p = subprocess.Popen(['git', "commit", "-eF", "-"], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _ = p.communicate(input=message.encode("utf-8"))[0]


def amend_commit(message: str) -> None:
    """
    Creates a commit with the given message.

    Set editor by setting the EDITOR environment variable.

    Args:
        message: The commit message.

    Returns:
        None
    """
    p = subprocess.Popen(['git', "commit", "--amend", "-e", "-F", "-"], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _ = p.communicate(input=message.encode("utf-8"))[0]


@dataclass
class Commit:
    commit_hash: str
    author: str
    date: str
    message: str
    diff: str

    def __str__(self):
        return f"{self.commit_hash} {self.author} {self.date}\n{self.message}"


def parse_commit(commit_text: str) -> Commit:
    commit_and_diff = re.split("\n(?=diff --git)", commit_text)
    commit_text = commit_and_diff[0]
    lines = commit_text.strip().split("\n")
    # Merge commits dont have a diff
    diff = commit_and_diff[1] if len(commit_and_diff) > 1 else ""
    return Commit(
        commit_hash=lines[0].split(" ")[1],
        author=lines[1].replace("Author: ", ""),
        date=lines[2].replace("Date:   ", ""),
        message="\n".join([line.strip() for line in lines[4:]]),
        diff=diff,
    )


def parse_git_log(log_data) -> list[Commit]:
    commits = re.split("\n(?=commit)", log_data)
    return [parse_commit(commit_text=commit) for commit in commits]


def last_commit() -> Commit:
    show = subprocess.check_output(["git", "show"])
    show_text = show.decode("utf-8")
    return parse_commit(show_text)


def latest_commits(n: int) -> list[Commit]:
    """
    Returns the latest n commits as a list of Commit objects.
    Args:
        n: The number of commits to return.
    Returns:
        A list of Commit objects.
    """
    log_data = subprocess.check_output(["git", "log", "-p", "-{}".format(n)]).decode("utf-8").strip()
    commits = re.split("\n(?=commit)", log_data)
    return [parse_commit(commit_text=commit) for commit in commits]
