# Quill NLP Tools and Datasets
Notebooks, scrapers, corpora, and utilities built and maintained Quill.org.

## About the Repo
This repo contains all of our data for Quill.org's machine learning models. This includes both grammar models that will be used across multiple products, and the algorthims for Quill Comprehension, a product that builds critical thinking skills. Quill Comprehension uses a topic classification algorthim to identify the main pieces of evidence in a student's writing in order to serve feedback that pushes the student to use more precise evidence.


## Quill Comprehension's Grading Logic
To understand the grading process for Quill Comprehension, please click on the link below to see a document that explains the steps of the grading process. To process this data, Quill first uses a script that helps us extract features from the student's writing for both the data labelling process and the machine learning models. This script incorporates AllenNLP. You can find an explanation of what the script does, and why each step is necessary. [Find the document here.](https://www.notion.so/Quill-Comprehension-Grading-Logic-395e3ba566484790a9187ddeb7cdfc6a#e34312ec6830435ba5e1c5b70737898e)


## Structure

```bash
.
├── data            # data we use for our experiments
    ├── interim     # preprocessed data
    ├── raw         # original, unprocessed data
    └── validated   # validated gold standard data for evaluation
│
├── demo            # D3 visualization that demonstrates NLP capabilities
├── experiments     # the json configuration files for our experiments
├── genmodel
├── models          # saved models for classification and other NLP tasks
├── notebooks       # Jupyter notebooks for data exploration & simple experiments
├── quillnlp        # the main package with the NLP code, including the dataset readers,
│                   # models and predictors for AllenNLP
├── scrapers        # data collection tools
├── scripts         # scripts for data processing, etc.
├── tests           # unit and more high-level tests
├── utils           # useful tools and scripts including document parsing
├── LICENSE
├── README.md       # this file
└── __init__.py
```

## Show version control how to deal with ipynb files

```bash
$ # ensure you are in the top level of the project before running these commands
$
$ source activate <YOUR CONDA ENV>
$ conda install -c conda-forge nbstripout
$ nbstripout --install
$ nbstripout --install --attributes .gitattributes
```

Running the above commands will ensure generated output from the notebooks is
not versioned, but that regular code changes will still be reflected.

Note: this means that switching branches could mean changes to notebook state.
Be aware of this and don't be alarmed.

## Experiments how-to

### Set up

#### Run the install script
```
sh bootstrap.sh
```
This will install python and all of the required dependencies, mostly within a virtual environment. This script should be idempotent and can be run multiple times without messing up your environment (It will update your dependencies though).

### Experiments

Experiments follow the general pattern:

1. Start Virtual Environment.
2. **Run Experiments/Training.**
3. Close Virtual Environment.

Start a virtual environment with:

```
source env/bin/activate
```

Close it with:

```
deactivate
```

**Note, if you are doing multiple experiments, you can open the environment, do a bunch of stuff, and then close the environment.**

#### Preparing Data

1. Put all labelled data in a file. This should be a tab-separated file
with two columns. The first column contains the sentence (prompt and response),
the second column contains the label. Save this file in the directory `data/raw`

2. Process the file with the script `create_train_and_test_data`:

From the directory root:
```
source env/bin/activate
```
```
python scripts/create_train_and_test_data.py --input_file data/raw/example.tsv

```

This will create three ndjson files in the `data/interim` directory: a train file
with the training data, a dev file with the development data and a test file with
the test data.

#### Run the baseline experiments:

```python scripts/train_baseline.py --train data/interim/example_train.ndjson --test data/interim/example_test.ndjson```

This will train a simple classifier. After evaluation, it prints out an
accuracy and performance per label.

#### Run the AllenNLP experiments.

Download the Glove 6B 300 data set **(800MB)** from this [website](https://nlp.stanford.edu/projects/glove/)

Here is the direct [800 MB download link](http://nlp.stanford.edu/data/glove.6B.zip)

Create a configuration file in the `experiments` directory. Start from
`example.json`, where you fill in the paths to your train, dev (validation)
and test files. If your machine does not have a GPU, set `cuda_device` (towards
the bottom) to `-1`. Otherwise, set it to 0. Since our experiments are small,
they can be run without a GPU. Also, update the `example.json` to point to the glove data set on your laptop.

#### Train an AllenNLP model:

```allennlp train experiments/example.json -s /tmp/example --include-package quillnlp```

Evaluate the AllenNLP model. We have our own script for this,
`evaluate_topic_classification`, which takes as first argument the test file,
and as second argument the directory where the model was saved:

```python3 -m scripts.evaluate_topic_classification data/interim/example_test.ndjson /tmp/example/```

#### Run the Google Sentence Encoder scripts:

```python3 scripts/sentence_encoder_tests.py --train data/interim/example_train.ndjson --dev data/interim/example_dev.ndjson --test data/interim/example_test.ndjson --out /tmp/classifier```

#### Deactivate the virtual environment:

```deactivate```