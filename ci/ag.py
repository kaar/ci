import logging
import os
from typing import Optional

import click

from ci import cmd

LOGGER = logging.getLogger(__name__)


def setup_logging():
    DEBUG = os.environ.get("DEBUG", False)
    log_level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER.debug("Debug mode enabled")


@click.group()
def cli():
    setup_logging()
    pass


@click.group("review")
def cmd_review():
    """Code review"""


@cmd_review.command("file")
@click.argument("file", required=False)
def cmd_review_file(file):
    cmd.review.file(file)


@cmd_review.command("pr")
def cmd_review_pr():
    """Review pull request"""
    # TODO: Implement pull request review
    click.echo("Pull request")


@cmd_review.command("diff")
@click.argument("commit_hash", required=False)
@click.option("--cached", is_flag=True)
def cmd_review_diff(commit_hash: Optional[str], cached: bool):
    if cached:
        cmd.review.cached()
    elif commit_hash:
        cmd.review.commit(commit_hash)
    else:
        # Example: `git dc | gi review diff`
        cmd.review.stdin()


@click.command()
def aliases():
    """Manage model aliases"""
    click.echo("Managing model aliases...")


@click.command()
@click.option("--amend", is_flag=True)
@click.option("--history", is_flag=False, default=0)
def ci(amend: bool, history: int):
    """Commit"""
    if amend:
        cmd.commit.amend_commit()
    else:
        cmd.commit.create_new_commit(history)


@click.command()
@click.argument("commit_hash", required=False, default="HEAD")
def show(commit_hash: str):
    """Show commit"""
    cmd.show.show(commit_hash)


@click.command()
@click.argument("file_path", required=False)
@click.option("--patch", "-p", is_flag=True)
def add(file_path: Optional[str], patch: bool):
    """Add commit"""
    cmd.add.add(file_path, patch=patch)


@click.command("dc")
def diff_cached():
    """Show cached diff"""
    cmd.diff.cached()


@click.command("st")
@click.argument("file_path", required=False)
def status(file_path: Optional[str]):
    """Show status"""
    cmd.status.status(file_path)


cli.add_command(aliases)
cli.add_command(ci)
cli.add_command(cmd_review)
cli.add_command(show)
cli.add_command(add)
cli.add_command(diff_cached)
cli.add_command(status)
if __name__ == '__main__':
    cli()
