import os
import openai
import jsonlines

from sklearn.metrics import classification_report, precision_recall_fscore_support

openai.api_key=os.environ['OPENAI_API_KEY']

# Step 1: create train, validation and test files
def prepare_data_for_finetuning(train_file):

    output_file = train_file.replace('.jsonl', '_ft.jsonl')
    with jsonlines.open(train_file) as reader, jsonlines.open(output_file, 'w') as writer:
        for item in reader:
            writer.write({
                'prompt': item['text'] + '\n\n###\n\n',
                'completion': ' ' + item['label']
            })

# Step 2: Finetune
def upload_file(filename):
    """ Uploads a file to OpenAI """
    openai.File.create(file=open(filename), purpose="classifications")


def get_number_of_classes(train_file):
    with jsonlines.open(train_file) as reader:
        classes = set([item['label'] for item in reader])

    print('Classes:', classes)
    print('Number:', len(classes))


def finetune(train_file_id, validation_file_id, model, num_classes):
    r = openai.FineTune.create(training_file=train_file_id, validation_file=validation_file_id, model=model)
    print(r)


# Step 3: classify test file
def find_matching_label(completion, label_list):
    for label in label_list:
        if completion.strip().startswith(label):
            return label
    return 'None'


def classify_ft(test_file, model_id, output_filename):

    correct = 0
    total = 0

    predicted_labels, correct_labels = [], []

    with jsonlines.open(output_filename, 'w') as writer:
        with jsonlines.open(test_file) as reader:

            test_items = list(reader)

            labels = list(set([item['completion'].strip() for item in test_items]))

            for item in test_items:
                total += 1

                r = openai.Completion.create(
                        model=model_id,
                        prompt=item['prompt'],
                        temperature=0)

                writer.write(r)
                choices = r.get('choices')
                if len(choices) > 0:
                    correct_label = item['completion'].strip()
                    prediction = find_matching_label(choices[0]['text'].strip(), labels)
                    correct_labels.append(correct_label)
                    predicted_labels.append(prediction)

                    if prediction == correct_label:
                        correct += 1

                print(r)

    print('Accuracy:', correct/total)

    report = classification_report(correct_labels, predicted_labels)
    print(report)

    results = precision_recall_fscore_support(correct_labels, predicted_labels, average='micro')

    print('P:', results[0])
    print('R:', results[1])
    print('F:', results[2])



for data_split in ['train', 'validation', 'test']:
    prepare_data_for_finetuning(f'esports_but_v3_{data_split}.jsonl')


classify_ft('sharks_but_v2_test_ft.jsonl',
            'ada:ft-quill-2023-02-23-10-08-38',
            'sharks_but_v2_test_ft_ada.jsonl')
