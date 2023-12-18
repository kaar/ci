import datetime
import json
from dataclasses import asdict, dataclass, field
from typing import Optional
import logging


import openai

LOGGER = logging.getLogger(__name__)


class Models:
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-1106-preview"

    DEFAULT_MODEL = GPT_4_TURBO


@dataclass
class Message:
    """
    A chat message sent to or received from the OpenAI API.
    """

    content: str
    """
    The content of the message.
    """

    role: str
    """
    The role of the message. Either "user" or "assistant".
    """


@dataclass
class SystemMessage(Message):
    """
    A system message sent to the OpenAI API.
    """

    role: str = "system"


@dataclass
class UserMessage(Message):
    """
    A user message sent to the OpenAI API.
    """

    role: str = "user"


@dataclass
class AssistantMessage(Message):
    """
    A message received from the OpenAI API.
    """

    role: str = "assistant"


@dataclass
class ChatRequest:
    """
    Creates a completion for the chat message
    """

    model: str
    """
    ID of the model to use. Currently, only gpt-3.5-turbo and
    gpt-3.5-turbo-0301 are supported.
    """

    messages: list[Message]
    """
    The messages to generate chat completions for, in the chat format.

    https://platform.openai.com/docs/guides/chat/introduction
    """

    temperature: Optional[float] = 1

    """
    What sampling temperature to use, between 0 and 2. Higher values
    like 0.8 will make the output more random, while lower values like
    0.2 will make it more focused and deterministic.

    We generally recommend altering this or top_p but not both.
    """

    top_p: Optional[float] = 1
    """
    An alternative to sampling with temperature, called nucleus sampling,
    where the model considers the results of the tokens with top_p
    probability mass. So 0.1 means only the tokens comprising the top 10%
    probability mass are considered.

    We generally recommend altering this or temperature but not both.
    """

    n: Optional[int] = 1
    """
    How many completions to generate for each prompt.

    Note: Because this parameter generates many completions, it can
    quickly consume your token quota. Use carefully and ensure that you
    have reasonable settings for max_tokens and stop.
    """

    stream: Optional[bool] = False
    """
    Whether to stream back partial progress. If set, tokens will be sent as
    data-only server-sent events as they become available, with the stream
    terminated by a data: [DONE] message.

    https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
    """

    stop: Optional[str] | list[str] | None = None
    """
    Up to 4 sequences where the API will stop generating further tokens. The
    returned text will not contain the stop sequence.
    """

    max_tokens: Optional[int] = None
    """
    The maximum number of tokens to generate in the completion.

    The token count of your prompt plus max_tokens cannot exceed the
    model's context length. Most models have a context length of 2048
    tokens (except for the newest models, which support 4096).

    https://platform.openai.com/tokenizer
    """

    presence_penalty: Optional[float] = 0
    """
    Number between -2.0 and 2.0. Positive values penalize new tokens based on
    whether they appear in the text so far, increasing the model's likelihood
    to talk about new topics.

    https://platform.openai.com/docs/api-reference/parameter-details
    """

    frequency_penalty: Optional[float] = 0
    """
    Number between -2.0 and 2.0. Positive values penalize new tokens based
    on their existing frequency in the text so far, decreasing the model's
    likelihood to repeat the same line verbatim.

    https://platform.openai.com/docs/api-reference/parameter-details
    """

    logit_bias: Optional[dict] = field(default_factory=dict)
    """
    Modify the likelihood of specified tokens appearing in the completion.

    Accepts a json object that maps tokens (specified by their token
    ID in the tokenizer) to an associated bias value from -100 to
    100. Mathematically, the bias is added to the logits generated by
    the model prior to sampling. The exact effect will vary per model,
    but values between -1 and 1 should decrease or increase likelihood
    of selection; values like -100 or 100 should result in a ban or
    exclusive selection of the relevant token.
    """

    user: Optional[str] = None
    """
    A unique identifier representing your end-user, which can help OpenAI
    to monitor and detect abuse.

    https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids
    """

    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=2)


@dataclass
class ChatCompletionResponse:
    """
    Response from the OpenAI API for a chat completion request.
    """

    @dataclass
    class Choices:
        message: Message
        index: int
        logprobs: Optional[dict]
        finish_reason: str


        def __post_init__(self):
            if isinstance(self.message, dict):
                self.message = Message(**self.message)

    @dataclass
    class Usage:
        prompt_tokens: int
        completion_tokens: int
        total_tokens: int

    id: str
    object: str
    created: datetime.datetime
    model: str
    choices: list[Choices]
    usage: Usage
    system_fingerprint: str

    def __post_init__(self):
        if isinstance(self.created, int):
            self.created = datetime.datetime.fromtimestamp(self.created)

        if isinstance(self.choices, list):
            self.choices = [self.Choices(**choice) for choice in self.choices if isinstance(choice, dict)]

        if isinstance(self.usage, dict):
            self.usage = self.Usage(**self.usage)

    @property
    def message(self) -> Message:
        return self.choices[0].message


def chat_completion(request: ChatRequest) -> ChatCompletionResponse:
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

    LOGGER.debug(response)

    return ChatCompletionResponse(**response)
