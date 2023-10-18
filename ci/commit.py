from ci import git, llm, models


def commit_history():
    max_diff_length = 2500
    history = []
    for c in git.latest_commits(5):
        if len(c.diff) > max_diff_length:
            continue
        history.append(models.UserMessage(c.diff))
        history.append(models.AssistantMessage(c.message))

    return history


def new():
    input_diff = git.cached_diff()
    commit_msg = llm.commit_msg(input_diff, history=[])
    git.create_commit(commit_msg)


def amend():
    last_commit = git.last_commit()
    input_diff = git.cached_diff()

    commit_msg = llm.amend_commit(last_commit.message, input_diff)

    git.amend_commit(commit_msg)
