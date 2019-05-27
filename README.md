# Quill NLP Tools and Datasets

Notebooks, scrapers, corpora, and utilities built and maintained Quill.org.


## Structure

```bash
.
├── LICENSE
├── README.md
├── __init__.py
├── data
├── models
├── notebooks
├── scrapers
├── tests
└── utils
```

Here is some information about each.

 * **data.** structured and unstructured documents
 * **models.** generated tensorflow models
 * **notebooks.** jupyter notebooks
 * **scrapers.** data collection tools
 * **tests.** high level tests
 * **utils.** useful tools and scripts including document parsing

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


## Run AllenNLP Experiments

### Training

allennlp train experiments/junkfood_because_topic_classifier_cpu.json -s /tmp/junkfood_because/ --include-package quillnlp

### Prediction

allennlp predict /tmp/junkfood_because/model.tar.gz data/interim/junkfood_because_test.ndjson --include-package quillnlp --predictor topic_classifier

### Evaluation

- with AllenNLP:

allennlp evaluate /tmp/junkfood_but_coref/model.tar.gz data/interim/junkfood_but_test.ndjson --include-package quillnlp

- with our own custom script:

python scripts/evaluate_topic_classification.py data/interim/junkfood_because_test.ndjson /tmp/junkfood_because/model.tar.gz



### Demo

python -m allennlp.service.server_simple --archive-path /tmp/junkfood_because/model.tar.gz --field-name text --port 8234 --predictor topic_classifier --include-package quillnlp
