import spacy
import json
import ndjson
import click
from tqdm import tqdm


@click.command()
@click.argument('input_file')
def run(input_file):
    output_file = input_file.replace('.ndjson', '_filtered.ndjson')

    grammar_model_path = '20230317/model/model-best/'
    nlp = spacy.load(grammar_model_path)

    with open(input_file) as i:
        try:
            data = ndjson.load(i)
        except json.decoder.JSONDecodeError:
            data = []
            with open(input_file) as i2:
                for line in i2:
                    if len(line.strip()) > 0:
                        data.append(json.loads(line.strip()))

    filtered_data = []
    for item in tqdm(data):
        original_sentence = item[1].get('original', item[0])

        doc = nlp(original_sentence)
        if doc.ents:
            print(item)
        else:
            filtered_data.append(item)

    with open(output_file, 'w') as o:
        ndjson.dump(filtered_data, o)


if __name__ == '__main__':
    run()