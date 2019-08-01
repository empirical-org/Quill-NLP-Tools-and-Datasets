""" Script to create synthetic data on the basis of backtranslation
with Google translate. Use as follows:

> python scripts/create_synthetic_data.py --lang nl --filename data_file.txt

lang: the language via which to do the backtranslation
data_file: the source file that will be translated line per line

To connect with Google Translate, the environment variable
GOOGLE_APPLICATION_CREDENTIALS needs to refer to the key file
"""

import os

import ndjson
import click
from google.cloud import translate

# Instantiates a client
translate_client = translate.Client()


@click.command()
@click.option('--lang', help='The language via which to do the backtranslation')
@click.option('--filename', help='The input file')
def generate(filename, lang):
    with open(filename) as i:
        items = ndjson.load(i)

    translated_items = []
    for item in items:
        translation = translate_client.translate(item["text"], target_language=lang)
        back_translation = translate_client.translate(translation["translatedText"],
                                                      target_language="en")

        print(item["text"])
        print(translation["translatedText"])
        print(back_translation["translatedText"])
        print("")

        translated_items.append({"text": back_translation["translatedText"],
                                 "label": item["label"]})

    basename = os.path.basename(filename)
    basename_without_extension = os.path.splitext(basename)[0]
    output_name = "{}_{}.ndjson".format(basename_without_extension, lang)

    with open(output_name, "w") as o:
        ndjson.dump(translated_items, o)


if __name__ == '__main__':
    generate()
