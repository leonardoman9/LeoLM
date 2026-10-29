from leolm.session import ConversationContext


def test_context_reuses_turns_and_expires():
    now = [0.0]
    context = ConversationContext(timeout=600, clock=lambda: now[0])
    context.add_turn("ciao", "salve")
    now[0] = 599
    assert len(context.messages()) == 2
    now[0] = 600
    assert context.messages() == []


def test_in_flight_turn_is_not_expired():
    now = [600.0]
    context = ConversationContext(timeout=600, clock=lambda: now[0], turns=[{"role": "user", "content": "ciao"}], last_activity=0)
    assert context.expire_if_idle(in_flight=True) is False
    assert context.turns
