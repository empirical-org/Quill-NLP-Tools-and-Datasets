# Quill NLP Tools and Datasets
Notebooks, scrapers, corpora, and utilities built and maintained Quill.org.

## About the Repo
This repo contains all of our data for Quill.org's machine learning models. This includes both grammar models that will be used across multiple products, and the algorthims for Quill Comprehension, a product that builds critical thinking skills. Quill Comprehension uses a topic classification algorthim to identify the main pieces of evidence in a student's writing in order to serve feedback that pushes the student to use more precise evidence.

## GPT scripts

### finetuning script
First, this repo contains a script to finetune a GPT-3.5-turbo model with Quill's human feedback. This can be done with the script `finetune.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/finetune.py output_file.json
```

### test script

Second, it is possible to evaluate GPT-3.5, GPT-4 or a finetuned model by comparing their feedback to Quill's human feedback, using `test_openai_for_feedback.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/test_openai_for_feedback.py model tag_for_output_file
```

