from qfragment.subject_verb_agreement import check_agreement
import pytest

sentences = [
        ("The scientist stirs the potion", True),
        ("Dancing in the moonlight makes me happy.", True),
        ("Dancing in the moonlight could rock.", True),
        ("Dancing in the moonlight rock.", False),
        ("Run around the word", True),
        ("Ran around the word", True),
        ("Have run around the word", True),
        ("Have mixed the potion", True),
        ("Running around the word", True),
        ("Will run around the word", True),
        ("Will have mixed the potion", True),
        ("Will have run around the word", True),
        ("Katherine began", True),
        ("Katherine started", True),
        ("Katherine start", False),
        ("Katherine started crying", True),
        ("Katherine began crying", True),
        ("Katherine began to cry", True),
        ("Katherine began cry", False),
        ("Katherine started cry", False),
        ("Katherine cried", True),
        ("Katherine crying", True),
        ("The men will be worry", False),
        ("The men will be irate", True),
        ("The men will be jumpy", True),
        ("The scientists will", True),
        ("The scientist will", True),
        ("The scientist stir the potion", False),
        ("The scientist and the boy stir the potion", True),
        ("The scientist and the boy stirs the potion", False),
        ("The scientist, along with the boy, stirs the potion", True),
        ("The scientist, along with the boy, stir the potion", False),
        ("The scientists stir the potion", True),
        ("The scientists stirs the potion", False),
        ("The scientists stir", True),
        ("The scientists stirs", False),
        ("He stirs the potion", True),
        ("He stir the potion", False),
        ("He and the boy stir the potion", True),
        ("He and the boy stirs the potion", False),
        ("He, along with the boy, stirs the potion", True),
        ("He, along with the boy, stir the potion", False),
        ("They stir the potion", True),
        ("They stirs the potion", False),
        ("They stir", True),
        ("They stirs", False),
        ("I stirs the potion", False),
        ("I stir the potion", True),
        ("The boy and I stir the potion", True),
        ("The boy and I stirs the potion", False),
        ("The boy, along with me, stirs the potion", True),
        ("The boy, along with me, stir the potion", False),
        ("We stir the potion", True),
        ("We stirs the potion", False),
        ("We stir", True),
        ("We stirs", False),
        ("You stirs the potion", False),
        ("You stir the potion", True),
        ("The boy and you stir the potion", True),
        ("The boy and you stirs the potion", False),
        ("The boy, along with you, stirs the potion", True),
        ("The boy, along with you, stir the potion", False),
        ("You stir", True),
        ("You stirs", False),
        ("You will stirs the potion", False),
        ("You will stir the potion", True),
        ("The boy and you will stir the potion", True),
        ("The boy and you will stirs the potion", False),
        ("The boy, along with you, will stirs the potion", False),
        ("The boy, along with you, will stir the potion", True),
        ("You will stir", True),
        ("You will stirs", False),
        ("The scientist will stir the potion", True),
        ("The men will be", True),
        ("The men will be worried", True),
        ("The men will be worrying", True),
        ("The men will be worried about her", True),
        ("The men will be worrying about her", True),
        ("The scientist will stirs the potion", False),
        ("The scientist and the boy will stir the potion", True),
        ("The scientist and the boy will stirs the potion", False),
        ("The scientist, along with the boy, will stir the potion", True),
        ("The scientist, along with the boy, will stirs the potion", False),
        ("The scientists will stir the potion", True),
        ("The scientists will stirs the potion", False),
        ("The scientists will stir", True),
        ("The scientists will stirs", False),
        ("The scientist will be", True),
        ("The scientist will be stirring the potion", True),
        ("The scientist will be stirs the potion", False),
        ("The scientist will be stir the potion", False),
        ("The scientist will be stirred the potion", False),
        ("The scientist will be worried the potion is not done", True),
        ("The scientist will be worrying the potion", True),
        ("The scientist and the boy will be stirring the potion", True),
        ("The scientist and the boy will be stirs the potion", False),
        ("The scientist, along with the boy, will be stirring the potion", True),
        ("The scientist, along with the boy, will be stirred the potion", False),
        ("The scientists will be stirring the potion", True),
        ("The scientists will be stirring", True),
        ("The scientists will be stirred", True),
        ("The scientists will be worried", True),
        ("The scientists will be worrying", True),
        ("The scientists will be stir", False),
        ("The scientists will be run out of town", True),
        ("The scientist has be stirring the potion", False),
        ("The scientist have been stirring the potion", False),
        ("The scientist has been stirring the potion", True),
        ("The scientist has been stirs the potion", False),
        ("The scientist has been stirred the potion", False),
        ("The potions have been stirred", True),
        ("The potions has been stirred", False),
        ("The potion has been stirred", True),
        ("The potion have been stirred", False),
        ("The scientist and the boy have been stirring the potion", True),
        ("The scientist and the boy has been stirring the potion", False),
        ("The scientist, along with the boy, has been stirring the potion", True),
        ("The scientist, along with the boy, have been stirring the potion", False),
        ("The scientists have been stirring", True),
        ("The scientists have been worried", True),
        ("The scientists have been stirred", True),
        ("The scientists have been swam", False),
        ("The scientists have been swimming", True),
        ("The scientists have been stir", False),
        ("The scientist has been stir", False),
        ("The scientist is stirring", True),
        ("The scientist was stirring", True),
        ("The scientists are stirring", True),
        ("The scientists were stirring", True),
        ("The races have been run", True),
        ("The races has been run", False),
        ("The race has been run", True),
        ("The race have been run", False),
        ("The scientists has been stirring", False),
        ("The scientist has been stirring", True),
        ("The scientist have been stirring", False),
        ("Worried about the world", True),
        ("Worrying needlessly", True),
        ("Until Sam is full grown", True),
        ("In the distance was the three forts whose historic names were known"
                "to every child in Charleston.", False),
        ("In the distance were the three forts whose historic names were known"
                "to every child in Charleston.", True),
        ("In the distance was three forts.", False),
        ("In the distance were three forts.", True),
        ("And with her pretty soft black curls, her rosy cheeks and pleasant"
                "voice, no one could imagined a more desirable teacher than"
                "Miss Rosalie George.", False),
        ("And with her pretty soft black curls, her rosy cheeks and pleasant"
                "voice, no one could imagine a more desirable teacher than"
                "Miss Rosalie George.", True),
        ("And with her pretty soft black curls, her rosy cheeks and pleasant"
                "voice, no one could have imagined a more desirable teacher than"
                "Miss Rosalie George.", True),
        ("And with her pretty soft black curls, her rosy cheeks and pleasant"
                "voice, no one could have imagine a more desirable teacher than"
                "Miss Rosalie George.", False),
        ("There am just twelve little girls in her school.", False),
        ("There were just twelve little girls in her school.", True),
        ("He will have a comfortable home now.", True),
        ("They will have a comfortable home now.", True),
        ("Let us go back a week and record what passed at the last interview"
                "between Philip and his father before the latter passed into"
                "the state of unconsciousness which preceded death.", True),
]


@pytest.mark.parametrize("test_input,expected", sentences) 
def test_eval(test_input, expected):
    assert check_agreement(test_input) == expected 

