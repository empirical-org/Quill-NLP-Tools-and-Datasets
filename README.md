# Quill NLP Tools and Datasets

## Background: NLP at Quill

At Quill, we want to help students become better writers. More specifically, we are developing automatic methods for identifying the argumentation students use in their texts, and for checking the grammatical correctness of sentences. To this goal, we are using Natural Language Processing (NLP), the subfield of Artificial Intelligence that deals with the automatic processing of text.

### Grammar Correction

In Quill's [Reading for evidence](https://www.quill.org/tools/evidence), students read a nonfiction text and are asked to support a series of claims with evidence sourced form the text. First we want to check their responses for grammatical correctness. We're focusing in particular on a range of grammar errors that we frequently see in students’ writings, such as confusion between *it’s* and *its*, between *than* and *then*, between a possessive form (*year’s*) and a plural form of the same word (*years*), and subject-verb agreement errors. Our goal is to automatically spot these errors, so that we can inform students about them and ask them to correct the error.

To to this, we’re training machine learning models that automatically assign particular labels to words in a text. Training such a machine learning model for grammar correction is done by showing the computer thousands of example sentences where the grammar errors have already been labeled, and then evaluating to what degree the model is able to identify in sentences that have not been labeled yet.

Unfortunately, we don’t have thousands of example sentences at hand where the errors have already been identified. To deal with this challenge, we mainly work with so-called synthetic data &mdash; sentences from sources like Wikipedia where we’ve automatically replaced a word by an incorrect alternative. For example, by replacing _it’s_ by _its_ in the sentence _it’s a sunny day_, we’ve automatically created a grammar error and we can tell our model what word in the sentence is incorrect.

Since around 2012, neural networks are the standard model type for solving this type of task in NLP. In the last few years transformer models have emerged as the most popular type of neural network for language tasks. To train such models, we use spaCy, one of the most popular open-source NLP libraries.

This repository contains our code for generating synthetic data with the types of grammatical errors that we're interested in, and for creating a spaCy transformer model to find these errors automatically.

### Feedback

Second, we are investigating generative AI models to help students develop strong argumentation skills. These models should give custom, targeted feedback to the arguments in students' responses, so that students strengthen their reading comprehension and hone their writing skills. This repository contains the code for our experiments with OpenAI's GPT models in particular. These experiments are focused on both prompt engineering, where we feed GPT a custom prompt with elaborate instructions and examples, and model finetuning, where we finetune a custom GPT model to give relevant feedback to students.

## Setup

All scripts have been tested with Python 3.11.6 and pip 23.2.1.

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


## Grammar Correction: Technical Details

This repository contains the scripts for creating synthetic data and training a grammar model with spaCy.

### Grammar

Quill has developed a grammar pipeline that labels sentences with frequent grammar errors, such as subject-verb agreement errors and plural-possessive errors.
The goal is to give students feedback on their writing, so that they can correct grammatical errors.
This pipeline is a combination of simple rules and a machine-learning model. The machine-learning model is trained on a mix of real data from students and data with
synthetic grammar errors. This repository has the code for creating such synthetic grammar errors and preparing a training corpus for spaCy.

#### Data

##### Option 1: Get existing training data

All grammar errors in the grammar model that are identified with a machine-learning model already have synthetically generated data.
This data is stored in a Google Cloud bucket and can be pulled with our DVC account:

```
> dvc pull
```

The training data will be downloaded to the `data/training` directory of this repository.

##### Option 2: Generate synthetic data

Alternatively, it is possible to create new synthetic training data. Every grammar error has an `ErrorGenerator`
that takes an input sentence and inserts a synthetic error in that sentence (if possible). For example, the `SubjectVerbAgreementWithSimpleNounErrorGenerator`
takes a sentence and replaces the present verb by another verb form if the subject contains a simple noun. The README file in the directory `scripts/quillgrammar` contains more detailed information about this synthetic data generation.

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

#### SpaCy training corpus

We train our grammar model as a spaCy pipeline. As a result, we need to prepare a training and development corpus
that spaCy can work with. This is done in the script `prepare_spacy_grammar_corpus`.
This takes as its only argument the directory to which the corpus files will be written:

```bash
> export PYTHONPATH=.
> python scripts/quillgrammar/prepare_spaCy_grammar_corpus.py output_path
```

The list of synthetic error files that will be used for the corpus can be adapted in `scripts/quillgrammar/grammar_files.csv`.
This csv file contains a list of the error files that will be used, together with the number of training items and the number
of dev/test items that will be taken from the file. The more difficult the error, the more training (and dev/test) files we
collect.

This script has the following output:
- `<output_path>/dev.spacy`: a development file on which the grammar model will be tested repeatedly during training
- `<output_path>/test.spacy`: a test file that can be used for testing the grammar model after training
- `<outputpath>/train/*.spacy`: one or more training files on which the grammar model will train

#### Training

Now the grammar model can be trained with spaCy's standard training command:

```
spacy train config_distilbert.cfg --output output_path \
--paths.train <prepare_spacy_grammar_corpus.py's output.path>/train \
--paths.dev <prepare_spacy_grammar_corpus.py's output.path>/dev.spacy \
--gpu-id 0
```

With `config_distilbert.cfg` as a configuration file, this command trains a model from scratch with the training corpus in `paths.train`. With `config_distilbert_add.cfg` as a configuration file, spaCy will load an already trained model from the directory `quillgrammar/models/current`, and continue training on the data in `paths.train`. This is convenient if an
existing model needs to be updated with some additional (e.g. manually labelled Quill) data. To create a training corpus
with new Quill data, format the data like the other training files (see for example `data/training/quill_labels_20231101_train.ndjson`), and rerun the previous step (`prepare_spacy_training_corpus.py`) with only the new
files in `grammar_files.csv`.

## Large Language Models for Student Feedback: Technical Details

Second, this repository contains all data and scripts for our experiments with Large Language Models for student feedback.
The goal of this task is to provide automatic feedback on the content of student responses.
The files with examples of human feedback are in `data/automl`, organized by passage and prompt. The scripts are in `scripts/gpt`.

### GPT scripts

There are several scripts for our experiments with GPT:
- `finetune.py`: finetune a GPT model with Quill's feedback
- `test_openai_for_feedback.py`: evaluate the output of a large language model against Quill's feedback
- `moderate_feedbac.py`: moderate GPT feedback by an additional GPT step that removes undesired elements

#### Finetuning script

First, this repo contains a script to finetune a GPT-3.5-turbo model with Quill's human feedback. This can be done with the script `finetune.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/finetune.py <output_file>.json
```

#### Evaluation script

Second, it is possible to evaluate GPT-3.5, GPT-4 or a finetuned GPT model by comparing their feedback to Quill's human feedback, using `test_openai_for_feedback.py`:

```
> pip install -r requirements-gpt.txt
> export OPENAI_API_KEY=<YOUR_KEY>
> python scripts/gpt/test_openai_for_feedback.py <model> <tag_for_output_file>
```

For example:

```
> python scripts/test_openai_for_feedback.py gpt-3.5-turbo gpt3-5-turbo
```

#### Moderation script

Finally, the moderation script is a basic script that calls a GPT model to moderate automatic feedback. This moderation step can be necessary when GPT gives feedback that does not focus on argumentation: comments on spelling or grammar, clarity or conciceness, or when GPT gives away the correct answer. The moderation script takes one or more pieces of feedback as input, asks the GPT model to remove any undesired elements, and writes the output to a file. It is used in the following way:

```
> python scripts/moderate_feedback.py <gpt_model> <output_file> --verbose <True/False>
```

For example:

```
> python scripts/moderate_feedback.py gpt-4 feedback_output.csv --verbose False
```
