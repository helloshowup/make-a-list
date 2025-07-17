class RateLimitError(Exception):
    pass


class APIStatusError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class APIConnectionError(Exception):
    pass


class _Message:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Message(content)


class _Completions:
    def create(self, **params):
        prompt = params.get("messages")[0]["content"]
        content = params.get("messages")[1]["content"]
        return type(
            "Resp", (), {"choices": [_Choice(f"{content}[{prompt.strip()}]")]}
        )()


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class OpenAI:
    def __init__(self, api_key=None):
        self.chat = _Chat()
