# Print out prompts that were used for testing
#
# Example:
# > export PYTHONPATH=.
# > python scripts/print_prompts.py

import os
from pathlib import Path

import jsonlines
from tqdm import tqdm

from scripts.data.bereal import passage as passage_bereal
from scripts.data.berlin import passage as passage_berlin
from scripts.data.haiti import passage as passage_haiti
from scripts.data.pompeii import passage as passage_pompeii
from scripts.data.quokkas import passage as passage_quokkas
from scripts.data.surgebarriers import passage as passage_barriers
from scripts.data.villages import passage as passage_villages

# Include all passages that need to be tested
passages = [passage_barriers,
            passage_bereal,
            passage_berlin,
            passage_haiti,
            passage_pompeii,
            passage_quokkas,
            passage_villages]


conjunctions = ['because', 'but', 'so']

def read_file(filename: str):
    """ Reads an input jsonl file train/test/validation data.

    Args:
        filename (str): filename of the data file

    Returns:
        list: the train/test/validation items
    """
    items = []
    with jsonlines.open(filename) as reader:
        for item in reader:
            if 'prediction' in item:
                items.append((item['text'].replace('\n', ' '), item['label'], item['prediction']))
            else:
                items.append((item['text'].replace('\n', ' '), item['label']))

    return items


def create_openai_feedback_prompt(passage, conjunction, response, add_passage=True):

    quill_prompt = passage['prompts'][conjunction]
    plagiarism_passage = passage['plagiarism'][conjunction]
    label_info = passage['instructions'][conjunction]
    feedback = passage['feedback'][conjunction]
    examples = passage['examples'][conjunction]
    evaluation = False
    # evaluation = passage['evaluation'][conjunction] if 'evaluation' in passage and conjunction in passage['evaluation'] else {}

    prompt = f"You are a teacher, helping fifth-grade students improve their writing skills. " \
        "In this exercise, students have read a text and are asked to complete a sentence. " \
        "The goal is for you to give feedback on their response. " \

    prompt += f"\n\nThis is the sentence they are asked to complete: '{quill_prompt}'. "

    if add_passage:
        prompt += f'\n\nHere is the text students have read, separated by triple backticks: \n\n```{plagiarism_passage}```\n'

    prompt += "\n" + label_info

    prompt += """
These are general rules for your feedback:
- Do not give feedback about grammar, spelling or punctuation.
- Do not ask students to make sentences more clear and concise.
- Do not suggest a better answer."""

    prompt += "\n\nFirst paraphrase the sentence, and then give the correct feedback for the paraphrase. Your feedback should be copied from these examples:"

    for label in examples:
        label_feedback = feedback[label]
        for idx, example in enumerate(examples[label]):
            prompt += f"\n\nResponse: {example}"
            if evaluation:
                prompt += f"\nParaphrase: {evaluation[label][idx]}"
            prompt += f"\nFeedback: {label_feedback}"

    if evaluation:
        prompt += f'\n\nResponse: {response}\nParaphrase:'
    else:
        prompt += f'\n\nResponse: {response}\nFeedback:'

    return prompt


def run():
    for passage in passages:
        for conjunction in conjunctions:

            # Read the passage data
            passage_name = Path(passage['files'][conjunction]["test"]).stem.split('_')[0]
            test_items = read_file(passage['files'][conjunction]["test"])
            correct_feedback = passage['feedback'][conjunction]

            for item in tqdm(test_items, desc=passage_name):

                sentence = item[0]
                correct_label = item[1]

                full_prompt = create_openai_feedback_prompt(passage, conjunction, sentence, add_passage=True)
                results_filename = f"prompt_{passage_name}_{conjunction}.txt"
                with open(results_filename, 'w') as results_file:
                    results_file.write(full_prompt)



if __name__ == '__main__':
    run()
