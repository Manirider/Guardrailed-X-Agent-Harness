from src.harness.tool_registry import ToolRegistry


def test_allowed():
    assert ToolRegistry.is_allowed("post_tweet")
    assert ToolRegistry.is_allowed("login")
    assert not ToolRegistry.is_allowed("follow")
