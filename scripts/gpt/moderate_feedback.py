# Simple script for moderating feedback with a GPT model. Takes Quill feedback as input, asks the
# GPT model to remove any undesired elements, and writes the output to a file.
#
# Usage:
# > python scripts/moderate_feedback.py <gpt_model> <output_file> --verbose <True/False>
# Example:
# > python scripts/moderate_feedback.py gpt-4 feedback_output.csv --verbose False


import os
import openai
import csv
import time
import click

from tqdm import tqdm
from scripts.data.bereal import passage

openai.api_key = os.getenv("OPENAI_API_KEY")

OPTIMAL_LABEL = 'Optimal'
SUBOPTIMAL_LABEL = 'Suboptimal'

INPUTFILE = 'data/automl/problematic_feedback.csv'

def read_file(filename):
    """ Reads problematic feedback from the input file."""
    items = []
    seen_feedback = set()
    with open(filename) as i:
        reader = csv.reader(i, delimiter=",")
        next(reader)
        for line in reader:
            feedback = line[2]
            if feedback not in seen_feedback:
                items.append(line[:3])
                seen_feedback.update([feedback])

    return items


def get_prompt(feedback):
    """ Assembles the prompt for feedback moderation. """

    prompt = """Correct the feedback below. Keep it as intact as possible, but remove any of the following sentences:
- sentences that refer to grammar, spelling or punctuation,
- sentences that say the response is unclear or not concise enough,
- sentences that give away the correct answer explicitly,
- feedback that asks the student to write two sentences instead of one.

If there is more than one question in the feedback, only keep the first question.

Keep the feedback as intact as possible. In particular, keep the first sentences. Do not remove:
- "Try clearing your response",
- "Check that your response only uses information from the text",
- "Now add another reason".

Here are some examples:
Feedback: Try clearing your response and starting again. Your response is too long and confusing. Focus on one specific contrast to the fact that many tourists enjoy taking quokka selfies.
Corrected feedback: Try clearing your response and starting again. Focus on one specific contrast to the fact that many tourists enjoy taking quokka selfies.

Feedback: Good start! You mentioned that it's possible to post later than two minutes, but can you explain why this is a contrast to the idea that BeReal is more authentic? Also, be sure to revise your response for clarity and grammar.
Corrected Feedback: Good start! You mentioned that it's possible to post later than two minutes, but can you explain why this is a contrast to the idea that BeReal is more authentic?

Feedback: You have the right idea! Now be more specific. Quokka bites can be a potential risk. How many people are bitten by quokkas each year?
Corrected feedback: You have the right idea! Now be more specific. Quokka bites can be a potential risk. How many people are bitten by quokkas each year?

Feedback: You have the right idea! Now be more specific. Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?
Corrected feedback: You have the right idea! Now be more specific. Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?

"""
    prompt += f"Feedback: {feedback}\n"
    prompt += f"Corrected feedback:"
    return prompt


def moderate(feedback, model):
    """ Ask GPT to rewrite a piece of feedback and return the answer."""
    full_prompt = get_prompt(feedback)

    messages = [
        {"role": "system", "content": full_prompt},
    ]
    try:
        response = openai.ChatCompletion.create(
                    model=model,
                    temperature=0,
                    max_tokens=175,
                    messages = messages
                    )
    except:
        time.sleep(3)
        response = openai.ChatCompletion.create(
                    model=model,
                    temperature=0,
                    max_tokens=75,
                    messages = messages
                    )

    answer = response['choices'][0]['message']['content'].replace('`', '')
    return answer


@click.command()
@click.argument('model')
@click.argument('output_file')
@click.option('--verbose', default=False)
def main(output_file, model, verbose):
    test_items = read_file(INPUTFILE)
    print("Test feedback items:", len(test_items))

    corrected = 0
    with open(output_file, 'w') as o:
        writer = csv.writer(o, delimiter=',')
        writer.writerow(['sentence', 'label', 'GPT feedback', 'Moderated feedback'])

        for item in tqdm(test_items):

            sentence = item[0]
            correct_label = item[1]
            feedback = item[2]

            if 'Feedback:' in feedback:
                feedback = feedback.split('Feedback:')[1].strip()

            answer = moderate(feedback, model)
            writer.writerow(item + [answer])

            if feedback != answer:
                if verbose:
                    print(feedback)
                    print('=>')
                    print(answer)
                    print('----')
                corrected +=1

        print('Corrected:', corrected, '/', len(test_items), '=', corrected/len(test_items)*100, '%')


if __name__ == "__main__":
    main()