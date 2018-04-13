# content of test_expectation.py
import pytest
from qfragment import detect_missing_verb

@pytest.mark.parametrize("test_input,expected", [
    ("Katherine was crying", False),
    ("Rainbows as blue as can be danced in the distance.", False),
    ("He ordered his sandwich with cheese.", False),
    ("Katherine crying", True),
    ("Rainbows as blue as.", True),
    ("With cheese", True),
])
def test_missing_verb(test_input, expected):
    assert detect_missing_verb(test_input) == expected
