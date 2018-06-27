# Test Job 1 

A job to test if we can generate models

```
genmodel/
  jobs/
    <SOME-JOB-NAME>/
      README.md
      playbook.yml
      droplet.yml
      labeled_data.csv
      reducer/
        reducer.py
        requirements.txt
        ... [other files needed for reduction]
      vectorizer/
        vectorizer.py
        requirements.txt
        ... [other files needed for vectorization]
```

### jobs/<SOME-JOB-NAME>

+ **README.md**. information about the job
+ **playbook.yml**. an ansible playbook descriping how to configure the servers
  that will run the reducers and vectorizers
+ **droplet.yml**. a description of the digital ocean droplet that the reducers
  and vectorizers will run on.
+ **labled_data.csv**. a csv file with two columns, data and label

### jobs/<SOME-JOB-NAME>/reducer

includes reducer.py, a requirements.txt, and any files reducer.py relies on.

### jobs/<SOME-JOB-NAME>/vectorizer

includes vectorizer.py, a requirements.txt, and any files vectorizer.py relies on.

