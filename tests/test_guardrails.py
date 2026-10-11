from src.harness.guardrails import GuardrailChain


def test_length_pass():
    g = GuardrailChain()
    res = g.check("short", "short")
    assert res.length_passed
    assert res.passed

def test_length_fail():
    g = GuardrailChain()
    res = g.check("short", "a"*281)
    assert not res.length_passed
    assert not res.passed

def test_banned_word():
    g = GuardrailChain()
    res = g.check("text", "this has guarantee")
    assert not res.banned_words_passed
    assert "banned_word:guarantee" in res.failure_reasons

def test_groundedness_url_introduced():
    g = GuardrailChain()
    res = g.check("Visit https://example.com", "Visit https://evil.com")
    assert not res.groundedness_passed
    assert "introduced_url" in res.failure_reasons

def test_groundedness_mention_introduced():
    g = GuardrailChain()
    res = g.check("Hello @alice", "Hello @bob")
    assert not res.groundedness_passed
