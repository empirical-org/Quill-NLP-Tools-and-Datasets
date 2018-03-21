# QFragment 

A library from Quill.org for detecting and correcting sentence fragments.

**NOTE:** word to to wise, this library is currently very unstable; be aware
that all updates could include breaking changes while we are in development.  If
you wish to use this library, please be sure to note the version you are using
and stick with it -- but come back often as great new functionality will be
added often!

## Installation

```bash
pip install qfragment
```

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

