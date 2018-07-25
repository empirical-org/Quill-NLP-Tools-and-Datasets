# Project Gutennberg File Downloader

This handy package makes it easy to do various bulk downloads from project
Gutenberg.

## Installation

```bash
pip install gutenfetch
```

## Usage

On the command line,
```
gutenfetch bookshelf 'http://www.gutenberg.org/wiki/Category:Children%27s_Bookshelf' childrens_books
```

## Configuration

To specify a regular output directory for the gutenfetch generated directory set
the environment variable GUTENFETCH_OUTPUT_DIR,

```bash
export GUTENFETCH_OUTPUT_DIR=/Users/you/Documents/gutenberg/books

```

if this variable is not set the output folder will end up in your current
directory.

To specify a max filename length, set GUTENFETCH_MAX_FILENAME_LEN
```bash
export GUTENFETCH_MAX_FILENAME_LEN=30
```
the default is 30. *Going very high can cause errors to occur!*
