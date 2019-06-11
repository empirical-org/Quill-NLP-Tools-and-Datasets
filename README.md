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

