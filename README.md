# Quill NLP Tools and Datasets

Notebooks, scrapers, corpora, and utilities built and maintained Quill.org.


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

