import re
import subprocess
from dataclasses import dataclass
from typing import Optional


def add(file_path: Optional[str], patch: bool = False) -> None:
    """
    Adds a file to the git index.

    Args:
        file_path: The path to the file to add.
        patch: If true, add interactively.

    Returns:
        None
    """
    cmd = ["git", "add"]
    if patch:
        cmd.append("-p")
    if file_path:
        cmd.append(file_path)
    subprocess.check_call(cmd)


def status(file_path: Optional[str]) -> str:
    """
    Returns the output of `git status`.

    Returns:
        The output of `git status`.
    """
    cmd = ["git", "status"]
    if file_path:
        cmd.append(file_path)

    return subprocess.check_output(cmd).decode("utf-8")


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


def validate_commit_hash(commit_hash: str) -> bool:
    if commit_hash.startswith("HEAD"):
        return True

    return bool(re.match(r'^[0-9a-f]{7,40}$', commit_hash))


def commit_hash_exists(commit_hash: str) -> bool:
    """
    Returns True if the commit hash exists in the git repository.

    git rev-parse --verify <commit_hash>
    """
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", commit_hash])
        return True
    except subprocess.CalledProcessError:
        return False


def show(commit_hash: str) -> str:
    # TODO: Handle command injection, this may not be enough.
    if not validate_commit_hash(commit_hash):
        raise ValueError(f"Invalid commit hash {commit_hash}")

    cmd = ["git", "show", commit_hash]
    diff = subprocess.check_output(cmd)
    return diff.decode("utf-8")


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
