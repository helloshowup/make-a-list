"""OpenAI chat completion client utilities."""

from __future__ import annotations

from typing import Iterable
import time

import openai

from .config import OPENAI_API_KEY

# Instantiate a single client for reuse
_client = openai.OpenAI(api_key=OPENAI_API_KEY)


def _chat_request(messages: Iterable[dict], model: str, temperature: float):
    """Send a chat completion request with retry logic."""
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            response = _client.chat.completions.create(
                model=model,
                messages=list(messages),
                temperature=temperature,
            )
            return response.choices[0].message.content
        except openai.RateLimitError as exc:
            last_exc = exc
        except openai.APIStatusError as exc:
            last_exc = exc
            if exc.status_code not in {429, 502}:
                raise
        if attempt < 2:
            time.sleep(2**attempt)
    # If we fall through, raise the last captured exception
    if last_exc:
        raise last_exc
    raise RuntimeError("Unknown error sending prompt")


def send_prompt(prompt: str, content: str, model: str = "o3", temp: float = 0.2) -> str:
    """Send `content` with a system `prompt` and return the assistant message text."""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content},
    ]
    return _chat_request(messages, model=model, temperature=temp)
