# Feedback script for OpenAI models.
#
# Usage:
# > python scripts/test_openai_for_feedback.py model tag_for_output_file
#
# Example:
# > python scripts/test_openai_for_feedback.py gpt-3.5-turbo gpt3-5-turbo


import os
import click
import openai
import jsonlines
import re
import tiktoken
import csv
import time
import threading

from tqdm import tqdm
from pathlib import Path
from scripts.data.bereal import passage as passage_bereal
from scripts.data.berlin import passage as passage_berlin
from scripts.data.haiti import passage as passage_haiti
from scripts.data.pompeii import passage as passage_pompeii
from scripts.data.quokkas import passage as passage_quokkas
from scripts.data.surgebarriers import passage as passage_barriers
from scripts.data.villages import passage as passage_villages



openai.api_key = os.getenv("OPENAI_API_KEY")

OPTIMAL_LABEL = 'Optimal'
SUBOPTIMAL_LABEL = 'Suboptimal'

OUTPUT_TOKENS = 75
MAX_RETRIES = 5

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


def map_label(label: str):
    """ Maps the label of an item (e.g. Label_1) to the
    corresponding binary label Optimal/Suboptimal.

    Args:
        label (str): the original label

    Returns:
        str: the corresponding binary label
    """
    if label.startswith('Label'):
        return SUBOPTIMAL_LABEL
    return OPTIMAL_LABEL



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


def is_optimal(feedback: str):
    """ Determines whether a piece of feedback corresponds to an optimal label.
    This is the case when it starts with Nice work, great job, etc.

    Args:
        feedback (str): the piece of feedback given by the model

    Returns:
        boolean: True if the feedback is Optimal, False otherwise
    """
    return 'Nice work!' in feedback or 'Great job!' in feedback or 'Excellent job' in feedback or 'Good job' in feedback


def fetch_with_timeout(api_call_func, messages, model, timeout_duration=10):
    """ Calls the provided API function with a timeout.

    Args:
        api_call_func (function): the API call function
        messages (list): the messages that will be sent to the API
        model (str): the model that will be used
        timeout_duration (int, optional): The length of the timeout. Defaults to 10.

    Returns:
        dict: a dict with the response returned by the API embedded
    """

    result_container = {"result": None, "is_done": False}

    def worker():
        result_container["result"] = api_call_func(messages, model)
        result_container["is_done"] = True

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=timeout_duration)

    if result_container["is_done"]:
        return result_container["result"]
    else:
        return None



def api_call_completion(messages, model):
    """ The API call for Completion models (such as GPT-3.5-turbo-instruct)

    Args:
        messages (list): the messages that will be sent to the API
        model (str): the model that will be used

    Returns:
        dict: the response returned by the API
    """

    return openai.Completion.create(
        model=model,
        prompt=messages[0]['content'],
        max_tokens=7,
        temperature=0
        )


def api_call_chat(messages, model):
    """ The API call for ChatCompletion models (such as GPT-3.5-turbo)

    Args:
        messages (list): the messages that will be sent to the API
        model (str): the model that will be used

    Returns:
        dict: the response returned by the API
    """

    return openai.ChatCompletion.create(
        model=model,
        temperature=0,
        max_tokens=OUTPUT_TOKENS,
        messages = messages
        )


@click.command()
@click.argument('model')
@click.argument('tag')
def run(model, tag):

    print('Running evaluation with model:', model)

    # Create and initialize results file
    results_filename = f"results_{tag}.txt"
    with open(results_filename, 'w') as results_file:
        results_file.write(f'Results for {model}\n')

    for passage in passages:
        for conjunction in conjunctions:

            # Read the passage data
            passage_name = Path(passage['files'][conjunction]["test"]).stem.split('_')[0]
            test_items = read_file(passage['files'][conjunction]["test"])
            correct_feedback = passage['feedback'][conjunction]

            # If we have fewer than 100 test items, we add the validation items
            # to the test set.
            if len(test_items) < 100:
                validation_items = read_file(passage['files'][conjunction]["validation"])
                test_items += validation_items

            tokens_per_prompt = []  # the number of tokens per prompt
            cost_per_prompt = []  # the API cost per prompt
            regex_hits = 0  # the number of times the regex for unwanted feedback fires
            identical_feedback = 0  # the number of times the LLM returns feedback identical to ours
            all_feedback = []  # all feedback

            # Initialize the confusion matrix
            confusion = {
                OPTIMAL_LABEL: {
                    OPTIMAL_LABEL: 0,
                    SUBOPTIMAL_LABEL: 0
                    },
                SUBOPTIMAL_LABEL: {
                    OPTIMAL_LABEL: 0,
                    SUBOPTIMAL_LABEL: 0
                }
            }

            outputfile = passage['files'][conjunction]["test"].replace('.jsonl', f'_{tag}.csv')
            with open(outputfile, 'w') as o:
                writer = csv.writer(o, delimiter=',')
                writer.writerow(['sentence', 'label', 'GPT feedback', 'evaluation'])

                for item in tqdm(test_items, desc=passage_name):

                    sentence = item[0]
                    correct_label = item[1]

                    full_prompt = create_openai_feedback_prompt(passage, conjunction, sentence, add_passage=True)

                    # Avoid GPT-4 rate limits
                    if model.startswith('gpt-4'):
                        time.sleep(7)

                    messages = [
                        {"role": "system", "content": full_prompt},
                    ]

                    for _ in range(MAX_RETRIES):
                        time.sleep(1)
                        if model == 'gpt-3.5-turbo-instruct':
                            response = fetch_with_timeout(api_call_completion, messages, model, timeout_duration=10)
                        else:
                            response = fetch_with_timeout(api_call_chat, messages, model, timeout_duration=10)

                        if response:
                            break

                    if 'message' in response['choices'][0]:
                        # For ChatCompletion models
                        answer = response['choices'][0]['message']['content']
                    else:
                        # For Completion models (such as GPT-3.5-turbo-instruct)
                        answer = response['choices'][0]['text']

                    feedback = answer.split('Feedback:')[1].strip() if 'Feedback:' in answer else answer
                    all_feedback.append(feedback)

                    # Compute the cost of the API call
                    encoding = tiktoken.get_encoding('cl100k_base')
                    num_tokens_prompt = sum([len(encoding.encode(m['content'])) for m in messages])
                    num_tokens_answer = len(encoding.encode(answer))
                    tokens_per_prompt.append((num_tokens_prompt + num_tokens_answer))
                    cost = (num_tokens_prompt + num_tokens_answer) / 1000 * 0.002
                    cost_per_prompt.append(cost)

                    writer.writerow((sentence, correct_label, answer))

                    if feedback == correct_feedback[correct_label]:
                        identical_feedback += 1

                    if re.search('((un)?clear\W|grammar|spelling|punctuation|concise|for example|(consider) (includ|add|mention)|incomplete|(\?.*){2,}|”)', feedback):
                        regex_hits += 1

                    if correct_label.startswith('Optimal'):
                        if is_optimal(feedback):
                            confusion[OPTIMAL_LABEL][OPTIMAL_LABEL] += 1
                        else:
                            confusion[OPTIMAL_LABEL][SUBOPTIMAL_LABEL] += 1
                    else:
                        if is_optimal(feedback):
                            confusion[SUBOPTIMAL_LABEL][OPTIMAL_LABEL] += 1
                        else:
                            confusion[SUBOPTIMAL_LABEL][SUBOPTIMAL_LABEL] += 1

            with open(results_filename, 'a') as results_file:
                results_file.write(f'=== {passage_name.upper()} - {conjunction.upper()} ===\n')
                results_file.write(f'Items: {len(all_feedback)}\n')
                results_file.write(f'Mean tokens per prompt: {sum(tokens_per_prompt)/len(tokens_per_prompt)}\n')
                results_file.write(f'Mean cost per prompt: {sum(cost_per_prompt)/len(cost_per_prompt)}\n')
                results_file.write(f'Cost for 50,000 requests: {sum(cost_per_prompt)/len(cost_per_prompt)*50000}\n')
                results_file.write(f'Unique feedback items: {len(set(all_feedback))}\n')
                results_file.write(f'Regex hits: {regex_hits} = {regex_hits/len(all_feedback)*100}%\n')
                results_file.write(f'Accuracy (identical): {identical_feedback/len(all_feedback)}\n')
                results_file.write(f'Accuracy (sub/optimal): {(confusion[OPTIMAL_LABEL][OPTIMAL_LABEL] + confusion[SUBOPTIMAL_LABEL][SUBOPTIMAL_LABEL])/len(all_feedback)}\n')
                results_file.write(f'Confusion matrix:\n')
                for label in [OPTIMAL_LABEL, SUBOPTIMAL_LABEL]:
                    results_file.write(f'{confusion[label][OPTIMAL_LABEL]}\t{confusion[label][SUBOPTIMAL_LABEL]}\n')



if __name__ == '__main__':
    run()
