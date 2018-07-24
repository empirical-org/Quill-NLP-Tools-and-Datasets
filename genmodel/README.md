# NLP Pipeline REST API

This is the nlp pipeline REST API.  Naming conventions are not entirely fixed
yet, so nlp job manager, and model generation pipeline probably refer to the
same thing.

The manager.py is a Flask API that runs on the nlp job manager digital ocean
droplet.  It communicates with a database that is set up according to the
specified configuration in the sql/ folder.

This folder also contains a script that can be used to kick off jobs.  It lives
in the jobs folder and has it's documentation with it.



