import openai

from .models import ChatRequest


def chat_completion(request: ChatRequest):
    messages: list[dict] = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in request.messages
    ]

    response = openai.ChatCompletion.create(
        model=request.model,
        messages=messages,
        temperature=request.temperature,
    )
    return response
