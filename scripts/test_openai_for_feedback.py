import os
import openai
import jsonlines
import requests
import random
import tiktoken
import csv
import time

from scripts.data.passages import passages, feedback_instructions

openai.api_key = os.getenv("OPENAI_API_KEY")
PALM_API_KEY = os.getenv("PALM_API_KEY")


OPTIMAL_LABEL = 'Optimal'
SUBOPTIMAL_LABEL = 'Suboptimal'

MODEL = "text-davinci-003"
MODEL = 'gpt-3.5-turbo'
MODEL = 'palm'

PASSAGE = 'quokkas'
CONJUNCTION = 'because'


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


def pick_random(items, label, number):
    candidate_items = [item[0] for item in items if item[1] == label]
    return random.choices(candidate_items, k=number)


def create_openai_feedback_prompt(prompt, passage, label_info, response):

        # "Please give feedback that is understandable and engaging for a fifth-grade student. " \
        # "Use simple language, clear explanations, and avoid complex vocabulary or concepts." \
        # "Try to keep responses concise and friendly, and stick to the examples as closely as possible." \


    prompt = f"You are a teacher, helping fifth-grade students improve their writing skills. " \
        "In this exercise, students have read a text and are asked to complete a sentence. " \
        "The goal is for you to give feedback on their response. " \
        f'\nHere is the text students have read, separated by triple backticks: \n```{passage}```\n' \
        f"\nThis is the sentence they are asked to complete: '{prompt}'.\n"

    prompt += label_info
    prompt += f'\nResponse: {response}\nFeedback:'

    return prompt


def create_conversation(prompt, passage, feedback_list, response):

    # "Please copy the most relevant example of feedback below. " \
    # "Please give feedback that is understandable and engaging for a fifth-grade student. " \
    # "Use simple language, clear explanations, and avoid complex vocabulary or concepts. " \
    # "Try to keep responses concise and friendly, and stick to the examples as closely as possible. " \
    # "Please copy one of the examples of feedback below. " \


    full_prompt = f"You are a teacher, helping fifth-grade students improve their writing skills. " \
        "In this exercise, students have read a text and are asked to complete a sentence. " \
        "Their response must use information from the text to explain why many tourists enjoy taking quokka selfies." \
        "The goal is for you to give feedback on that response. " \
        f'\nHere is the text students have read, separated by triple backticks: \n```{passage}```\n' \
        f"\nThis is the sentence they are asked to complete: '{prompt}'.\n"

    conversation = [{"role": "system", "content": full_prompt}]

    for item in feedback_list:
        conversation.append({"role": "user", "content": item["Response"]})
        conversation.append({"role": "assistant", "content": item["Label"] + "\n" + item["Feedback"]})

    conversation.append({"role": "user", "content": "Now copy the most relevant one from your previous responses for this student entry: " + response})

    return conversation


def evaluate_answer(answer, correct_label):
    if 'nice work' in answer.lower() and correct_label.startswith('Optimal'):
        return True
    elif "try clearing" in answer.lower() and correct_label.startswith('Label_0'):
        return True
    elif "right idea!" in answer.lower() and correct_label.startswith('Label_'):
        return True
    return False


train_items = read_file(passages[PASSAGE]['files'][CONJUNCTION]['train'], passages[PASSAGE]['prompts'][CONJUNCTION])
test_items = read_file(passages[PASSAGE]['files'][CONJUNCTION]['test'], passages[PASSAGE]['prompts'][CONJUNCTION])

# for item in test_items:
#     print(item[0])
# input()

print('Train items:', len(train_items))
print('Test items:', len(test_items))

final_output = []
tokens_per_prompt = []
cost_per_prompt = []
grammar = 0
for item in test_items:

    sentence = item[0]
    correct_label = item[1]
    automl_label = item[2]

    full_prompt = create_openai_feedback_prompt(passages[PASSAGE]['prompts'][CONJUNCTION], passages[PASSAGE]['plagiarism'][CONJUNCTION], passages[PASSAGE]['feedback'][CONJUNCTION], sentence)
    print(full_prompt)
    input()
    # conversation = create_conversation(passages[PASSAGE]['prompts'][CONJUNCTION], passages[PASSAGE]['plagiarism'][CONJUNCTION], passages[PASSAGE]['feedback_list'][CONJUNCTION], sentence)
    # for item in conversation:
    #     print(item)
    # input()

    if MODEL.startswith('gpt-3.5'):

        messages = [
            {"role": "system", "content": full_prompt},
        ]
        try:
            response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        temperature=0,
                        max_tokens=75,
                        messages = messages
                        )
        except:
            time.sleep(3)
            response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        temperature=0,
                        max_tokens=75,
                        messages = messages
                        )

        answer = response['choices'][0]['message']['content']

        if 'grammar' in answer:
            grammar += 1

        print('--')
        print(sentence)
        print(correct_label)
        print(answer)
        # input('')

        encoding = tiktoken.get_encoding('cl100k_base')
        # num_tokens_prompt = len(encoding.encode(full_prompt))
        num_tokens_prompt = sum([len(encoding.encode(m['content'])) for m in messages])
        num_tokens_answer = len(encoding.encode(answer))
        tokens_per_prompt.append((num_tokens_prompt + num_tokens_answer))

        cost = (num_tokens_prompt + num_tokens_answer) / 1000 * 0.002
        cost_per_prompt.append(cost)

        evaluation = evaluate_answer(answer, correct_label)

        final_output.append((sentence, correct_label, answer, evaluation))

    elif MODEL.startswith('palm'):

        data = {"prompt": {"text": full_prompt}}
        url = f'https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText?key={PALM_API_KEY}'

        r = requests.post(url, json=data)

        answer = r.json()['candidates'][0]['output']
        print(answer)

        evaluation = evaluate_answer(answer, correct_label)
        final_output.append((sentence, correct_label, answer, evaluation))

    else:
        response = openai.Completion.create(
            model=MODEL,
            prompt=full_prompt,
            temperature=0,
            max_tokens=10,
            top_p=1.0,
            stop=["\n"],
            n=1
        )

        print(response)

with open(passages[PASSAGE]['files'][CONJUNCTION]['test'].replace('_automl.jsonl', '_feedback_expl.csv'), 'w') as o:
    writer = csv.writer(o, delimiter=',')
    writer.writerow(['sentence', 'label', 'GPT feedback', 'evaluation'])
    for item in final_output:
        writer.writerow(item)


evaluations = [item[-1] for item in final_output]

# print("Suboptimal labeled as optimal:", confusion_matrix[SUBOPTIMAL_LABEL][OPTIMAL_LABEL])
print(f"Mean tokens per prompt:", sum(tokens_per_prompt)/len(tokens_per_prompt))
print(f"Mean cost per prompt:", sum(cost_per_prompt)/len(cost_per_prompt))
print("Cost for 50,000 requests:", sum(cost_per_prompt)/len(cost_per_prompt)*50000)
print('Accuracy:', sum(evaluations)/len(evaluations))
print('Mentions of grammar:', grammar)
