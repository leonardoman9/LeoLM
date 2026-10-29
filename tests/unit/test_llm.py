from types import SimpleNamespace

from leolm.llm import OpenRouterConversation


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": "risposta"}}]}


class FakeClient:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        self.calls += 1
        return FakeResponse()


class RetryClient:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        import requests
        self.calls += 1
        if self.calls < 3:
            raise requests.exceptions.Timeout()
        return FakeResponse()


def test_conversation_returns_reply_without_logging_secret():
    config = SimpleNamespace(conversation_api_key="secret", conversation_endpoint="https://example.test",
                             model="test", retry_count=2, retry_backoff=0, network_timeout=1)
    client = FakeClient()
    assert OpenRouterConversation(config, client=client).complete([]) == "risposta"
    assert client.calls == 1


def test_conversation_retries_at_most_two_times():
    config = SimpleNamespace(conversation_api_key="secret", conversation_endpoint="https://example.test",
                             model="test", retry_count=2, retry_backoff=0, network_timeout=1)
    client = RetryClient()
    assert OpenRouterConversation(config, client=client, sleeper=lambda _: None).complete([]) == "risposta"
    assert client.calls == 3
