from src.harness.guardrails import GuardrailChain


def test_url_preserved():
    g = GuardrailChain()
    res = g.check("https://a.com", "https://a.com")
    assert res.groundedness_passed

def test_mention_preserved():
    g = GuardrailChain()
    res = g.check("@alice", "@alice")
    assert res.groundedness_passed
