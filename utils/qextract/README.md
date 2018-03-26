# QExtract

This is a library for extracting clauses and phrases from existing sentences.
Right now it can extract participle phrases and subordinate clauses that begin
with a subordinate conjunction.  It is under development, and functionality will
continue to grow. 

It is maintained by Quill.org, a non-profit focused on helping
students become better writers.


## Installation

```sh
pip install qextract
python -m spacy download en
export QUILL_SPACY_MODEL=en
```

QUILL_SPACY_MODEL=en is the default, but en_core_web_lg or other models can be
specified using this web module.  Non-english models are not supported.

## Usage

**On the command line**,

A number of commands will be installed with qextract. extract_participle_phrases
and extract_subordinate_clauses are 2 of them. Here is an example of using
extract_participle_phrases.  For more info on any command do `command -h`.

```
extract_participle_phrases -i MYINPUTFILE.txt -o MYOUTPUTFILE.txt
```

Will produce the file MYOUTPUTFILE.txt. It will be formatted like this, 

```
Max, relying on instinct, gave the order.
relying on instinct
relying
False




They say, though, that misery itself, shared by two sympathetic souls, may be borne with patience."
shared by two sympathetic souls, may be borne with patience."
shared
False
```

where the pattern is,

```txt
Sentence
Participle Phrase
Participle verb
flagged




```

**More commands,**
 + extract_participle_phrases
 + extract_subordinate_clauses
 + more comming soon!

do -h on any command for info on how to use it.

