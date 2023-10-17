# Finetuning script for OpenAI models. Finetunes a GPT-3.5-turbo model on Quill's feedback.
#
# Usage: First set your OpenAI key, then run the script:
# > export OPENAI_API_KEY=<YOUR_KEY>
# > python scripts/finetune.py finetune_file.json

import os
import time
import openai
import click
import jsonlines
import random
import tiktoken
import threading
import numpy as np

from collections import defaultdict
from tqdm import tqdm

# from scripts.data.villages import passage as villages
from scripts.data.bereal import passage as bereal
from scripts.data.berlin import passage as berlin
from scripts.data.haiti import passage as haiti
from scripts.data.pompeii import passage as pompeii
from scripts.data.quokkas import passage as quokkas
from scripts.data.surgebarriers import passage as surgebarriers
from scripts.data.villages import passage as villages

OPTIMAL_LABEL = 'Optimal'
SUBOPTIMAL_LABEL = 'Suboptimal'
OUTPUT_TOKENS = 75
MAX_RETRIES = 5
MODEL = 'gpt-3.5-turbo-0613'
CONJUNCTIONS = ['because', 'but', 'so']


NUM_ITEMS = 10  # The number of finetuning examples to collect for every passage-conjunction combination.
FEEDBACK_SOURCE = 'quill'

passages = [berlin, haiti, pompeii, quokkas, surgebarriers, villages]
openai.api_key = os.getenv("OPENAI_API_KEY")
encoding = tiktoken.get_encoding("cl100k_base")

def read_file(filename, prompt):
    items = []
    with jsonlines.open(filename) as reader:
        for item in reader:
            if 'prediction' in item:
                items.append((item['text'].replace('\n', ' '), item['label'], item['prediction']))
            else:
                items.append((item['text'].replace('\n', ' '), item['label']))

    return items


def map_label(label):
    if label.startswith('Label'):
        return SUBOPTIMAL_LABEL
    return OPTIMAL_LABEL


def map_to_binary(items):
    new_items = []
    for item in items:
        if len(item) == 3:
            new_items.append((item[0], map_label(item[1]), map_label(item[2])))
        else:
            new_items.append((item[0], map_label(item[1])))

    return new_items


def create_openai_feedback_prompt(passage, response, conjunction, add_passage=True):

    # "Please give feedback that is understandable and engaging for a fifth-grade student. " \
    # "Use simple language, clear explanations, and avoid complex vocabulary or concepts." \
    # "Try to keep responses concise and friendly, and stick to the examples as closely as possible." \

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

    prompt += "\n\nYour feedback should be copied from these examples:"

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


#==================================================#
# OpenAI Functions. Taken from the OpenAI Cookbook #
#==================================================#

def check_data_format(dataset):
    # Format error checks
    format_errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in ("system", "user", "assistant"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            if not content or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")
    else:
        print("No errors found")


# not exact!
# simplified from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages, tokens_per_message=3, tokens_per_name=1):
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens

def num_assistant_tokens_from_messages(messages):
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(encoding.encode(message["content"]))
    return num_tokens

def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")


def check_token_count(dataset):
    # Warnings and tokens counts
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []

    for ex in dataset:
        messages = ex["messages"]
        if not any(message["role"] == "system" for message in messages):
            n_missing_system += 1
        if not any(message["role"] == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages))
        assistant_message_lens.append(num_assistant_tokens_from_messages(messages))

    print("Num examples missing system message:", n_missing_system)
    print("Num examples missing user message:", n_missing_user)
    print_distribution(n_messages, "num_messages_per_example")
    print_distribution(convo_lens, "num_total_tokens_per_example")
    print_distribution(assistant_message_lens, "num_assistant_tokens_per_example")
    n_too_long = sum(l > 4096 for l in convo_lens)
    print(f"\n{n_too_long} examples may be over the 4096 token limit, they will be truncated during fine-tuning")

    # Pricing and default n_epochs estimate
    MAX_TOKENS_PER_EXAMPLE = 4096

    TARGET_EPOCHS = 3
    MIN_TARGET_EXAMPLES = 100
    MAX_TARGET_EXAMPLES = 25000
    MIN_DEFAULT_EPOCHS = 1
    MAX_DEFAULT_EPOCHS = 25

    n_epochs = TARGET_EPOCHS
    n_train_examples = len(dataset)
    if n_train_examples * TARGET_EPOCHS < MIN_TARGET_EXAMPLES:
        n_epochs = min(MAX_DEFAULT_EPOCHS, MIN_TARGET_EXAMPLES // n_train_examples)
    elif n_train_examples * TARGET_EPOCHS > MAX_TARGET_EXAMPLES:
        n_epochs = max(MIN_DEFAULT_EPOCHS, MAX_TARGET_EXAMPLES // n_train_examples)

    n_billing_tokens_in_dataset = sum(min(MAX_TOKENS_PER_EXAMPLE, length) for length in convo_lens)
    print(f"Dataset has ~{n_billing_tokens_in_dataset} tokens that will be charged for during training")
    print(f"By default, you'll train for {n_epochs} epochs on this dataset")
    print(f"By default, you'll be charged for ~{n_epochs * n_billing_tokens_in_dataset} tokens")
    print(f"Estimated price: ${0.0080 * n_epochs * n_billing_tokens_in_dataset / 1000}")


def feedback_is_correct(feedback, correct_label):
    return correct_label.startswith('Optimal') and is_optimal(feedback) or (not correct_label.startswith('Optimal') and not is_optimal(feedback))



#=============#
# Main method #
#=============#

@click.command()
@click.argument('output_file')
def run(output_file):
    finetuning_examples = []
    for passage in passages:
        if 'files' in passage and 'prompts' in passage:
            for conjunction in ['because', 'but', 'so']:
                if conjunction in passage['files'] and conjunction in passage['prompts']:
                    print(passage['files'][conjunction]["train"])
                    train_items = read_file(passage['files'][conjunction]["train"], passage['prompts'][conjunction])
                    random.shuffle(train_items)

                    new_finetuning_examples = []

                    for train_item in train_items:
                        sentence = train_item[0]
                        correct_label = train_item[1]
                        quill_feedback = passage['feedback'][conjunction][correct_label]
                        full_prompt = create_openai_feedback_prompt(passage, sentence, conjunction, add_passage=True)

                        if FEEDBACK_SOURCE == 'quill':
                            messages = [
                                {"role": "system", "content": full_prompt},
                                {"role": "assistant", "content": quill_feedback},
                            ]
                            new_finetuning_examples.append({"messages": messages})
                        else:
                            auto_messages = [
                                {"role": "system", "content": full_prompt},
                            ]

                            for _ in range(MAX_RETRIES):
                                response = fetch_with_timeout(api_call_chat, auto_messages, 'gpt-4', timeout_duration=10)
                                if response:
                                    break
                                time.sleep(10)

                            answer = response['choices'][0]['message']['content']
                            feedback = answer.split('Feedback:')[1].strip() if 'Feedback:' in answer else answer

                            print(sentence)
                            print(feedback)
                            print(feedback_is_correct(feedback, correct_label))

                            if feedback_is_correct(feedback, correct_label):
                                messages = [
                                    {"role": "system", "content": full_prompt},
                                    {"role": "assistant", "content": quill_feedback},
                                ]

                                new_finetuning_examples.append({"messages": messages})

                        if len(new_finetuning_examples) >= NUM_ITEMS:
                            break

                    finetuning_examples.extend(new_finetuning_examples)

    print("Finetuning examples:", len(finetuning_examples))

    check_data_format(finetuning_examples)
    check_token_count(finetuning_examples)

    input("Press enter to continue")

    with jsonlines.open(output_file, 'w') as writer:
        for example in finetuning_examples:
            writer.write(example)

    input("Created finetuning file")

    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.File.create(
    file=open(output_file, "rb"),
    purpose='fine-tune'
    )

    ft_response = openai.FineTuningJob.create(training_file=response['id'],
        model="gpt-3.5-turbo",
        hyperparameters = {
            "n_epochs": 3
            }
        )
    print(ft_response)


if __name__ == '__main__':
    run()