# Quill NLP Tools and Datasets

This is the respository for Quill's NLP experiments. Most importantly, it contains the code for creating data with synthetic grammar errors, and our investigation of large language models for student feedback.

## Setup

Different scripts in this repo rely on different pip packages. We currently use python's `virtualenv` standard library to manage dependencies.

Here's how to set up the (currently) two virtual envs:

```shell
python -m venv env-grammar
python -m venv env-gpt
```

Here's how to use a virtualenv in the context of running a script:

```shell
source env-myEnvName/bin/activate
python myScript
deactivate
```

## Grammar

Quill has developed a grammar pipeline that labels sentences with frequent grammar errors, such as subject-verb agreement errors and plural-possessive errors.
The goal is to give students feedback on their writing, so that they can correct grammatical errors.
This pipeline is a combination of simple rules and a machine-learning model. The machine-learning model is trained on a mix of real data from students and data with
synthetic grammar errors. This repository has the code for creating such synthetic grammar errors and preparing a training corpus for spaCy.

### Data

#### Option 1: Get existing training data

All grammar errors in the grammar model that are identified with a machine-learning model already have synthetically generated data.
This data is stored in a Google Cloud bucket and can be pulled with our DVC account:

```
> dvc pull
```

The training data will be downloaded to the `data/training` directory of this repository.

#### Option 2: Generate synthetic data

Alternatively, it is possible to create new synthetic training data. Every grammar error has an `ErrorGenerator`
that takes an input sentence and inserts a synthetic error in that sentence (if possible). For example, the `SubjectVerbAgreementWithSimpleNounErrorGenerator`
takes a sentence and replaces the present verb by another verb form if the subject contains a simple noun.

The error generators can be run with the script `create_grammar_training_corpus.py`:

```bash
> export PYTHONPATH=.
> python scripts/quillgrammar/create_grammar_training_corpus.py \
path_to_newsoftheworld_corpus
```

It will generate a synthetic training file for each of the error generators that is called in the script.

Add this training data to the directory `data/training` and upload it to the Google Cloud with

```
> dvc commit
> dvc push
```

### SpaCy training corpus

We train our grammar model as a spaCy pipeline. As a result, we need to prepare a training and development corpus
that spaCy can work with. This is done in the script `prepare_spacy_grammar_corpus`.
This takes as its only argument the directory to which the corpus files will be written:

```bash
> export PYTHONPATH=.
> python scripts/quillgrammar/prepare_spaCy_grammar_corpus.py output_path
```

The list of synthetic error files that will be used for the corpus can be adapted in `scripts/quillgrammar/grammar_files.csv`.

### Training

Now the grammar model can be trained with spaCy's standard training command:

```
spacy train config_distilbert.cfg --output output_path \
--paths.train path_to_training_files --paths.dev dev_file --gpu-id 0
```

## Large Language Models for student feedback

Second, this corpus contains all data and scripts for our experiments with Large Language Models for student feedback.
The goal of this task is to provide automatic feedback on the content of student responses.
The files with examples of human feedback are in `data/automl`, organized by passage and prompt. The scripts are in `scripts/gpt`.

## GPT scripts

There is a script for finetuning a GPT model with Quill's feedback, and another one for evaluating the output of a large language model:

### finetuning script

First, this repo contains a script to finetune a GPT-3.5-turbo model with Quill's human feedback. This can be done with the script `finetune.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/finetune.py <output_file>.json
```

### test script

Second, it is possible to evaluate GPT-3.5, GPT-4 or a finetuned model by comparing their feedback to Quill's human feedback, using `test_openai_for_feedback.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/test_openai_for_feedback.py <model> <tag_for_output_file>
```

For example:

```
> python scripts/test_openai_for_feedback.py gpt-3.5-turbo gpt3-5-turbo
```
