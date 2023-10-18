from . import models, openai

DEFAULT_MODEL = "gpt-4"


def review(diff: str, model: str = DEFAULT_MODEL, temperature: float = 0.2) -> str:
    """
    This function takes a git diff as input and returns a code review
    as output.
    """
    instruction = """
You will receive a git diff.
Respond with a code review of the commit.
Look for bugs, security issues, and opportunities for improvement.
Provide short actionable comments with examples if needed.
If no issues are found, respond with "Looks good to me".
Use markdown to format your review.
"""

    response = openai.chat_completion(
        request=models.ChatRequest(
            model=model,
            messages=[
                models.SystemMessage(instruction),
                models.UserMessage(diff),
            ],
            temperature=temperature,
        )
    )
    msg = response.choices[0].message.content

    return msg


def commit_msg(
    input_diff: str,
    history: list,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
    """This function takes a git diff as input and returns a git commit message"""

    COMMIT_INSTRUCTION = """
You will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""
    history = history or []

    system_message = models.SystemMessage(COMMIT_INSTRUCTION)
    input_message = models.UserMessage(input_diff)

    response = openai.chat_completion(
        request=models.ChatRequest(
            model=model,
            messages=[
                system_message,
                *history,
                input_message,
            ],
            temperature=temperature,
        )
    )
    commit_msg = response.choices[0].message.content

    return commit_msg


def amend_commit(last_commit: str, diff: str, model: str = DEFAULT_MODEL, temperature: float = 0.2) -> str:
    COMMIT_INSTRUCTION = """
You will receive first receive the previous commit message.
Then you will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""
    response = openai.chat_completion(
        request=models.ChatRequest(
            model=model,
            messages=[
                models.SystemMessage(COMMIT_INSTRUCTION),
                models.UserMessage(last_commit),
                models.UserMessage(diff),
            ],
            temperature=temperature,
        )
    )
    commit_msg = response.choices[0].message.content
    return commit_msg
