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



