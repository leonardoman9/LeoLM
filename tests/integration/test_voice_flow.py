from leolm.session import VoiceSession
from tests.fakes.adapters import FakeConversation


def test_voice_flow_preserves_context_with_fake_adapters():
    remote = FakeConversation(["prima risposta", "seconda risposta"])
    session = VoiceSession(remote)
    assert session.process("prima domanda") == "prima risposta"
    assert session.process("seconda domanda") == "seconda risposta"
    assert remote.calls[1][0]["content"] == "prima domanda"
