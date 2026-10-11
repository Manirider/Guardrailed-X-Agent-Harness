import pytest
from src.harness.models import FormattedPost


def test_valid():
    fp = FormattedPost(tweet_text="hi", source_row_id="r1")
    assert fp.source_row_id == "r1"

def test_missing_field():
    with pytest.raises(Exception):
        FormattedPost(tweet_text="hi")
