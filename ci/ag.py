from typing import Optional

import click

from ci import commit, git, highlight, review


@click.group()
def cli():
    pass


@click.group("review")
def cmd_review():
    """Code review"""


@cmd_review.command("diff")
@click.argument("commit_hash", required=False)
@click.option("--cached", is_flag=True)
def cmd_review_diff(commit_hash: Optional[str], cached: bool):
    if cached:
        review.cached()
    elif commit_hash:
        review.commit(commit_hash)
    else:
        # Example: `git dc | gi review diff`
        review.stdin()


@click.command()
def aliases():
    """Manage model aliases"""
    click.echo("Managing model aliases...")


@click.command()
@click.option("--amend", is_flag=True)
def ci(amend: bool):
    """Commit"""
    if amend:
        commit.amend()
    else:
        commit.new()


@click.command()
@click.argument("commit_hash", required=False, default="HEAD")
def show(commit_hash: str):
    """Show commit"""
    click.echo(highlight.diff(git.show(commit_hash)))


@click.command()
@click.argument("file_path", required=False)
@click.option("--patch", "-p", is_flag=True)
def add(file_path: Optional[str], patch: bool):
    """Add commit"""
    git.add(file_path, patch=patch)


cli.add_command(aliases)
cli.add_command(ci)
cli.add_command(cmd_review)
cli.add_command(show)
cli.add_command(add)
if __name__ == '__main__':
    cli()
