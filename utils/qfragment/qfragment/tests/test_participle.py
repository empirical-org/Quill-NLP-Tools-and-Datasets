from qfragment import is_participle_clause_fragment
import pytest

participle_clauses = [
    "Worried about the world.", 
    "Worrying needlessly.",
    "Running out of excuses.",
    "According to his trusty servant Jeff.",
    "According to his trusty servant Jeff, who was very good at his job.",
    "Sprawled on the hot dirt like a lost slug.",
    "Thinking about her.",
    "Wishing that the day would end soon so he could return to his dog.",
    "Dead as a door nail",
    "Tired and needing sleep",
    "Tired and needing sleep, worried and wanting a friend.",
]

non_participle_clauses = [
    "Dancing in the moonlight rock",
    "John, tired and needing sleep, continued toward the gate.",
    "Tired and needing sleep, John continued toward the gate.",
    "Sleeping is one of the best parts of the day.",
    "Worrying about the state of the world is no fun.",
    "Jumping up and down could be exciting.",
    "Dreaming of his long lost sheep, Eli's eye's fluttered peacefully.",
    "Sick men are unpleasant.",
    "Dancing boys can never sing.",
    "Beautiful toy birds",
    "He is a great warrior",
    "Running is fun",
    "Swimming sucks",
] 


@pytest.mark.parametrize("test_input", participle_clauses) 
def test_participle_clauses_marked(test_input):
    assert is_participle_clause_fragment(test_input) >= .5 


@pytest.mark.parametrize("test_input", non_participle_clauses) 
def test_non_participle_clauses_not_marked(test_input):
    assert is_participle_clause_fragment(test_input) <= .5 
