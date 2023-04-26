import os
import openai
import jsonlines
import random
import tiktoken
import csv

from scripts.data.passages import passages

openai.api_key = os.getenv("OPENAI_API_KEY")

OPTIMAL_LABEL = 'Optimal'
SUBOPTIMAL_LABEL = 'Suboptimal'

MODEL = "text-davinci-003"
MODEL = 'gpt-3.5-turbo'

PASSAGE = 'quokkas'
CONJUNCTION = 'because'


def read_file(filename, prompt):
    items = []
    with jsonlines.open(filename) as reader:
        for item in reader:
            if 'prediction' in item:
                items.append((prompt + " " + item['text'].replace('\n', ' '), item['label'], item['prediction']))
            else:
                items.append((prompt + " " + item['text'].replace('\n', ' '), item['label']))

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


def create_openai_prompt(optimal_train_examples, suboptimal_train_examples, conjunction, passage, label_info):

    prompt = f"You are a teacher, helping students improve their writing skills. " \
        f"In this exercise, students have read the following text: \n{passage}\n" \
        f"\nNow they are asked to complete a sentence ending with '{conjunction}', basing themselves on the text.\n"

    prompt += label_info
    # prompt += "\n\nHere are some examples of optimal responses: "
    # for item in optimal_train_examples:
    #     prompt += '\n - ' + item

    # prompt += "\n\nHere are some examples of suboptimal responses: "

    # for item in suboptimal_train_examples:
    #     prompt += '\n - ' + item

    prompt += '\n\nNow please rate the following response as optimal or suboptimal:\n'

    return prompt


train_items = read_file(passages[PASSAGE]['files'][CONJUNCTION]['train'], passages[PASSAGE]['prompts'][CONJUNCTION])
test_items = read_file(passages[PASSAGE]['files'][CONJUNCTION]['test'], passages[PASSAGE]['prompts'][CONJUNCTION])

print('Train items:', len(train_items))
print('Test items:', len(test_items))

binary_train_items = map_to_binary(train_items)
binary_test_items = map_to_binary(test_items)

optimal_train_examples = pick_random(binary_train_items, OPTIMAL_LABEL, 10)
suboptimal_train_examples = pick_random(binary_train_items, SUBOPTIMAL_LABEL, 10)

# optimal_train_examples = [r for r_list in passages[PASSAGE]['example_responses'][CONJUNCTION][OPTIMAL_LABEL].values() for r in r_list]
# suboptimal_train_examples = [r for r_list in passages[PASSAGE]['example_responses'][CONJUNCTION][SUBOPTIMAL_LABEL].values() for r in r_list]

print(optimal_train_examples)
print(suboptimal_train_examples)

openai_prompt = create_openai_prompt(optimal_train_examples, suboptimal_train_examples, CONJUNCTION, passages[PASSAGE]['plagiarism'][CONJUNCTION], passages[PASSAGE]['suboptimal_correction'][CONJUNCTION])
print(openai_prompt)

input()

correct, total = 0, 0
test_set = binary_test_items
tokens_per_prompt = []
cost_per_prompt = []

confusion_matrix = {OPTIMAL_LABEL: {
                        OPTIMAL_LABEL: 0,
                        SUBOPTIMAL_LABEL: 0
                    },
                    SUBOPTIMAL_LABEL: {
                        OPTIMAL_LABEL: 0,
                        SUBOPTIMAL_LABEL: 0
                    }}

final_output = []
for item in binary_test_items:

    sentence = item[0]
    label = item[1]
    automl_label = item[2]

    full_prompt = openai_prompt + sentence

    if MODEL.startswith('gpt-3.5'):

        messages = [
            {"role": "user", "content": full_prompt},
        ]
        response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    max_tokens=200,
                    messages = messages
                    )

        answer = response['choices'][0]['message']['content']

        print('--')
        print(sentence)
        print(answer)

        encoding = tiktoken.get_encoding('cl100k_base')
        num_tokens_prompt = len(encoding.encode(full_prompt))
        num_tokens_answer = len(encoding.encode(answer))
        tokens_per_prompt.append((num_tokens_prompt + num_tokens_answer))

        cost = (num_tokens_prompt + num_tokens_answer) / 1000 * 0.002
        cost_per_prompt.append(cost)

        if SUBOPTIMAL_LABEL.lower() in answer.lower():
            answer = SUBOPTIMAL_LABEL
        else:
            answer = OPTIMAL_LABEL

        if answer == label:
            correct +=1
        else:
            print("GPT:", answer)
            print("Quill:", label)

        total +=1

        confusion_matrix[label][answer] += 1
        final_output.append((sentence, label, automl_label, answer))

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

with open(passages[PASSAGE]['files'][CONJUNCTION]['test'].replace('_automl.jsonl', '_all_plagiarism.csv'), 'w') as o:
    writer = csv.writer(o, delimiter=',')
    writer.writerow(['sentence', 'label', 'automl', 'gpt-3.5'])
    for item in final_output:
        writer.writerow(item)


print(f"Accuracy: {correct}/{total} = {correct/total}")
suboptimal_count = len([x for x in test_set if x[1] == SUBOPTIMAL_LABEL])
print(f"Baseline: {suboptimal_count}/{total} = {suboptimal_count/total}")
print("Optimal labeled as suboptimal:", confusion_matrix[OPTIMAL_LABEL][SUBOPTIMAL_LABEL])
print("Suboptimal labeled as optimal:", confusion_matrix[SUBOPTIMAL_LABEL][OPTIMAL_LABEL])
print(f"Mean tokens per prompt:", sum(tokens_per_prompt)/len(tokens_per_prompt))
print(f"Mean cost per prompt:", sum(cost_per_prompt)/len(cost_per_prompt))
print("Cost for 50,000 requests:", sum(cost_per_prompt)/len(cost_per_prompt)*50000)
