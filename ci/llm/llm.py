from . import openai


def code_review(
    code: str,
    model: str = openai.Models.DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
    instruction = """
Respond with a code review of the commit.
Look for bugs, security issues, and opportunities for improvement.
Provide short actionable comments with examples if needed.
Use markdown to format your review.
"""
    response = openai.chat_completion(
        request=openai.ChatRequest(
            model=model,
            messages=[
                openai.SystemMessage(instruction),
                openai.UserMessage(code),
            ],
            temperature=temperature,
        )
    )
    msg = response.choices[0].message.content

    return msg


def review(
    diff: str,
    model: str = openai.Models.DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
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
        request=openai.ChatRequest(
            model=model,
            messages=[
                openai.SystemMessage(instruction),
                openai.UserMessage(diff),
            ],
            temperature=temperature,
        )
    )
    msg = response.choices[0].message.content

    return msg


def commit_msg(
    input_diff: str,
    history: list,
    model: str = openai.Models.DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
    """This function takes a git diff as input and returns a git commit message"""

    COMMIT_INSTRUCTION = """
You will receive a git diff and respond with a git commit message.
Provide a clear and concise commit message that summarizes the changes made in this diff.
Separate subject from body with a blank line.
Limit the subject line to 50 characters.
Capitalize the subject line.
Do not end the subject line with a period.
Use the imperative mood in the subject line.
Wrap the body at 72 characters.
Use the body to explain what and why vs. how.
"""
    history = history or []

    system_message = openai.SystemMessage(COMMIT_INSTRUCTION)
    input_message = openai.UserMessage(input_diff)

    response = openai.chat_completion(
        request=openai.ChatRequest(
            model=model,
            messages=[
                system_message,
                input_message,
            ],
            temperature=temperature,
        )
    )
    commit_msg = response.choices[0].message.content

    return commit_msg


def amend_commit(
    last_commit: str,
    diff: str,
    model: str = openai.Models.DEFAULT_MODEL,
    temperature: float = 0.2,
) -> str:
    COMMIT_INSTRUCTION = """
You will receive first receive the previous commit message.
Then you will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
"""
    response = openai.chat_completion(
        request=openai.ChatRequest(
            model=model,
            messages=[
                openai.SystemMessage(COMMIT_INSTRUCTION),
                openai.UserMessage(last_commit),
                openai.UserMessage(diff),
            ],
            temperature=temperature,
        )
    )
    commit_msg = response.choices[0].message.content
    return commit_msg
