from subject_verb_agreement import check_agreement

# pip install pytest

sentences = [
        ("The scientist stirs the potion", True),
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
        ("The scientist will stirs the potion", False),
        ("The scientist and the boy will stir the potion", True),
        ("The scientist and the boy will stirs the potion", False),
        ("The scientist, along with the boy, will stir the potion", True),
        ("The scientist, along with the boy, will stirs the potion", False),
        ("The scientists will stir the potion", True),
        ("The scientists will stirs the potion", False),
        ("The scientists will stir", True),
        ("The scientists will stirs", False),
        ("The scientist will be stirring the potion", True),
        ("The scientist will be stirs the potion", False),
        ("The scientist will be stir the potion", False),
        ("The scientist will be stirred the potion", False),
        ("The scientist and the boy will be stirring the potion", True),
        ("The scientist and the boy will be stirs the potion", False),
        ("The scientist, along with the boy, will be stirring the potion", True),
        ("The scientist, along with the boy, will be stirred the potion", False),
        ("The scientists will be stirring the potion", True),
        ("The scientists will be stir the potion", False),
        ("The scientists will be stirring", True),
        ("The scientists will be stirred", True),
        ("The scientists will be stir", False),
        ("The scientist has be stirring the potion", False),
        ("The scientist have been stirring the potion", False),
        ("The scientist has been stirring the potion", True),
        ("The scientist has been stirs the potion", False),
        ("The scientist has been stirred the potion", False),
        ("The scientist and the boy have been stirring the potion", True),
        ("The scientist and the boy has been stirring the potion", False),
        ("The scientist, along with the boy, has been stirring the potion", True),
        ("The scientist, along with the boy, have been stirring the potion", False),
        ("The scientists have been stirring", True),
        ("The scientists have been worried", True),
        ("The scientists have been stirred", True),
        ("The scientists have been stir", False),
        ("The scientists has been stirring", False),
        ("The scientist has been stirring", True),
        ("The scientist have been stirring", False)
]
        
def test_answer():
    errors = 0
    for s,a in sentences:
        try:
            assert check_agreement(s) == a 
        except:
            errors += 1
            print('ERROR: expected {} for'.format(a))
            print(s)
            print('----') 
    print('Finished with {}/{}'.format(len(sentences) - errors, len(sentences)))


test_answer()
