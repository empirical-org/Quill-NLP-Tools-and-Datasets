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

Add the follwing lines to your .bash_profile or system equivalent
```bash
alias ltserver='nohup java -cp /opt/LanguageTool-4.1/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 </dev/null >/dev/null 2>&1 &'
export LT_PORT=8081
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
python -m spacy download en
export QUILL_SPACY_MODEL=en_core_web_md
```

QUILL_SPACY_MODEL is en_core_web_md by default. Some English spacy models are
not supported yet because spacy 2.x does not play well with TensorFlow.  We are
working on a work around for this; please be patient. 

## Usage

On the command line,
```
$ qfragment 'Until she leapt into the air and kissed him.'
This looks like a subordinating conjunction fragment. Try removing the
subordinating conjunction or adding a main clause.
$
$ qfragment 'She leapt into the air and kissed him.'
This looks like a strong sentence.
```

As a module,
```py
from qfragment import check

feedback  = check('Until she leapt into the air and kissed him.')

print(feedback.human_readable) # => This looks like a subordinating conjunction
                               #    fragment. Try removing the subordinating
                               #    conjunction or adding a main clause.
```

