# NLP Pipeline REST API

This is the nlp pipeline REST API.  Naming conventions are not entirely fixed
yet, so nlp job manager, and model generation pipeline probably refer to the
same thing.

The manager.py is a Flask API that runs on the nlp job manager digital ocean
droplet.  It communicates with a database that is set up according to the
specified configuration in the sql/ folder.

This folder also contains a script that can be used to kick off jobs.  It lives
in the jobs folder and has it's documentation with it.

## Running in production

In production, the server is gunicorn, we run the api using a command like
`gunicorn -w 4 -b 0.0.0.0:5000 manager:app` on the server.

## Training Jobs

In order to fully understand how the nlp pipeline works it is important to
understand the concept of a training job.  Training jobs use specify rules for
job creation and can be used in tandem with this api to launch nlp jobs that
produce useable models.  please see our [nlp pipeline example
job](https://github.com/empirical-org/nlp-example-job).

