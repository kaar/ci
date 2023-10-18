from ci import models, openai

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
