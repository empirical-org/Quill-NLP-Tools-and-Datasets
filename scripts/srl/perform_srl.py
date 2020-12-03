import json
import click

from quillnlp.preprocessing.srl import perform_srl


@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--prompt', default=None, help='An optional prompt')
def srl(input_file, output_file, prompt):

    print(prompt)
    with open(input_file) as i:
        responses = [line.strip() for line in i]

    results = perform_srl(responses, prompt)

    with open(output_file, "w") as o:
        json.dump(results, o)


if __name__ == "__main__":
    srl()
