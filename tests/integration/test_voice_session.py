from leolm.session import VoiceSession
from tests.fakes.adapters import FakeConversation


def test_voice_session_completes_and_returns_to_idle_contract():
    session = VoiceSession(FakeConversation(["risposta"]))
    assert session.process("comando") == "risposta"
    assert session.context.turns[-1]["role"] == "assistant"
