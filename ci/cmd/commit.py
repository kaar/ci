from ci import git, llm


def new():
    input_diff = git.cached_diff()
    commit_msg = llm.commit_msg(input_diff, history=[])
    git.create_commit(commit_msg)


def amend():
    last_commit = git.last_commit()
    input_diff = git.cached_diff()

    commit_msg = llm.amend_commit(last_commit.message, input_diff)

    git.amend_commit(commit_msg)
