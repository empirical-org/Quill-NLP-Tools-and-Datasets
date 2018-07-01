# Test Job 1 

This job is a demonstration job to show how this system works.

```
genmodel/
  jobs/
    <SOME-JOB-NAME>/
      README.md
      playbook.yml
      description.yml
      labeled_data.csv
      start.sh
      reducer/
        publisher.py
        reducer.py
        requirements.txt
        writer.py
        ... [other files needed for reduction]
      vectorizer/
        publisher.py
        requirements.txt
        vectorizer.py
        writer.py
        ... [other files needed for vectorization]
```

### jobs/<SOME-JOB-NAME>

+ **README.md**. information about the job
+ **playbook.yml**. an ansible playbook descriping how to configure the servers
  that will run the reducers and vectorizers
+ **droplet.yml**. a description of the digital ocean droplet that the reducers
  and vectorizers will run on.
+ **labled_data.csv**. a csv file with two columns, data and label
+ **start.sh**. Starts the reducers,  

### jobs/<SOME-JOB-NAME>/reducer

includes reducer.py, a requirements.txt, and any files reducer.py relies on. It
also includes a publisher and writer for the reducer that writes to the
database.

### jobs/<SOME-JOB-NAME>/vectorizer

includes vectorizer.py, a requirements.txt, and any files vectorizer.py relies
on. It also includes a publisher and writer for the vectorizer that writes to
the database.

