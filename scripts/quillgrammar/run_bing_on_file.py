import csv
import time
import click

from tqdm import tqdm

from quillnlp.spelling.bing import correct_sentence_with_bing


@click.command()
@click.argument('filename')
def correct(filename):

    with open(filename) as i:
        sentences = [line.strip() for line in i]

    output_file = filename.replace('.txt', '_bing.csv')

    with open(output_file, "w") as csv_out:
        writer = csv.writer(csv_out, delimiter="\t")
        for row in tqdm(sentences):

            sentence = row.strip()
            correct_sentence, response, output = correct_sentence_with_bing(sentence)

            output = [correct_sentence]
            for token in response.get('flaggedTokens', []):
                output.append(token['token'])
                output.append(token['suggestions'][0]['suggestion'])

            output.append(str(response))
            writer.writerow(output)


if __name__ == '__main__':
    correct()
