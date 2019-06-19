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

Make sure you have python3 installed on your machine.

1. Start a virtual environment and activate it: 

```
$virtualenv env --python python3
$source env/bin/activate
```

2. Install the required dependencies: 

```$pip install -r requirements.txt```

3. Prepare the data: 

3.1 Put all labelled data in a file. This should be a tab-separated file
with two columns. The first column contains the sentence (prompt and response),
the second column contains the label. Save this file in the directory `data/raw`

3.2 Process the file with the script `create_train_and_test_data`: 

```python scripts/create_train_and_test_data.py --input_file data/raw/example.tsv```

This will create three ndjson files in the `data/interim` directory: a train file
with the training data, a dev file with the development data and a test file with 
the test data.

3.3 Download the English spaCy model: 

```python -m spacy download en```

4. Run the baseline experiments:

```python scripts/train_baseline.py --train data/interim/example_train.ndjson --test data/interim/example_test.ndjson```

This will train a simple classifier. After evaluation, it prints out an 
accuracy and performance per label.

5. Run the AllenNLP experiments. 

5.1 Create a configuration file in the `experiments` directory. Start from 
`example.json`, where you fill in the paths to your train, dev (validation)
and test files. If your machine does not have a GPU, set `cuda_device` (towards
the bottom) to `-1`. Otherwise, set it to 0. Since our experiments are small,
they can be run without a GPU.

5.2 Train an AllenNLP model:

```allennlp train experiments/example.json -s /tmp/example --include-package quillnlp```

5.3 Evaluate the AllenNLP model. We have our own script for this,
`evaluate_topic_classification`, which takes as first argument the test file,
and as second argument the directory where the model was saved:

```python scripts/evaluate_topic_classification.py data/interim/example_test.ndjson /tmp/example/```

6. Run the Google Sentence Encoder scripts:

```python scripts/sentence_encoder_tests.py --train data/interim/example_train.ndjson --dev data/interim/example_dev.ndjson --test data/interim/example_est.ndjson --out /tmp/classifier```

7. Deactivate the virtual environment: 

```deactivate```