# QFragment 

A library from Quill.org for detecting and correcting sentence fragments.

**NOTE:** word to to wise, this library is currently very unstable; be aware
that all updates could include breaking changes while we are in development.  If
you wish to use this library, please be sure to note the version you are using
and stick with it -- but come back often as great new functionality will be
added often!

## Installation

1. Install languagetool

Qfragment relies on LanguageTool to function. LanguageTool is an open-source
grammar and spell-checker written in Java. In order to maximize performance, we
will run a languagetool server that QFragment will be able to connect to.

Change to the opt directory. If you don't have one create one.
```bash
cd /opt
```

Dowload languagetool to your current directory and uzip it.
```bash
sudo wget "https://languagetool.org/download/LanguageTool-4.1.zip"
sudo unzip LanguageTool-4.1.zip
sudo rm LanguageTool-4.1.zip
```

Add the follwing lines to your .bash_profile or system equivalent. Do not
include a trailing slash for the LT_URI.
```bash
alias ltserver='nohup java -cp /opt/LanguageTool-4.1/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 </dev/null >/dev/null 2>&1 &'
export LT_URI=http://localhost:8081
```

Start the server
```bash
ltserver
```

LanguageTool is now running on port 8081. To test that it works try hitting
http://localhost:8081/v2/check?language=en-US&text=my+text in your browser.

2. Install QFragment

```bash
pip install qfragment
```

QUILL_SPACY_MODEL is en_core_web_lg by default. If you wish to download another
model, do so with,

```bash
python -m spacy download <SPACY MODEL NAME>
```

and set

```bash
export QUILL_SPACY_MODEL=<SPACY_MODEL_NAME>
```

## Usage

As a module,
```py
from qfragment import check

feedback  = check('Until she leapt into the air and kissed him.')

print(feedback.human_readable) # => This looks like a subordinating conjunction
                               #    fragment. Try removing the subordinating
                               #    conjunction or adding a main clause.
```

On the command line,

 + command line use no longer available because of its startling poor
   performance. It may be reintroduced later.
