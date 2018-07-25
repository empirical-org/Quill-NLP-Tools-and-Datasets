from qfragment import detect_infinitive_phrase
import pytest

infinitive_phrases = [
    "To finish her shift without spilling another pizza into a customer's lap",
    "To win the approval of her mother",
    "to win the approval of her mother by switching her major from fine arts to pre-med.",
    "To survive Dr. Peterson's boring history lectures",
    "to understand the interplay of muscle and bone in the human body.",
    "To lick the grease from his shiny fingers despite the disapproving glances of his girlfriend Gloria",
    "To kick the ball past the dazed goalie",
    "To smash a spider",
    "Those basketball shoes, to be perfectly honest.",
    "To explain why he had brought Squeeze, his seven-foot pet python, to Mr. Parker's English class.",
    "To avoid burning another bag of popcorn.",
    "to be perfectly honest",
    "to flirt with the cute guys who congregate at the food court."
]

non_infinitive_phrases = [
    "Janice and her friends went to the mall to flirt with the cute guys who congregate at the food court.",
    "Those basketball shoes, to be perfectly honest, do not complement the suit you are planning to wear to the interview.",
    "To avoid burning another bag of popcorn, Brendan pressed his nose against the microwave door, sniffing suspiciously.",
    "Kelvin, an aspiring comic book artist, is taking Anatomy and Physiology this semester to understand the interplay of muscle and bone in the human body.",
    "The best way to survive Dr. Peterson's boring history lectures is a sharp pencil to stab in your thigh if you catch yourself drifting off.",
    "Lakesha hopes to win the approval of her mother by switching her major from fine arts to pre-med.",
    "To finish her shift without spilling another pizza into a customer's lap is Michelle's only goal tonight.",
] 


@pytest.mark.parametrize("test_input", infinitive_phrases) 
def test_participle_clauses_marked(test_input):
    assert detect_infinitive_phrase(test_input) == True 


@pytest.mark.parametrize("test_input", non_infinitive_phrases) 
def test_non_participle_clauses_not_marked(test_input):
    assert detect_infinitive_phrase(test_input) == False 
