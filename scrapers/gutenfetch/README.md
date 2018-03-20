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
