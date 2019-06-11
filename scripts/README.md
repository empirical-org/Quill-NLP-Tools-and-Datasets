This directory contains scripts for testing NLP functionality.

## Quill's Grading Logic
This script helps us extract features for both the data labelling process and the machine learning models. You can find an explanation of what the script does, and why each step is necessary. [Find the document here.](https://www.notion.so/Quill-Comprehension-Grading-Logic-395e3ba566484790a9187ddeb7cdfc6a#e34312ec6830435ba5e1c5b70737898e)

## Semantic Role Labelling

Semantic role labelling identifies the verbs in a sentence and the semantic roles that are associated with them.
These roles are:

- arg0: the 'agent': the entity that initiates an action
- arg1: the 'patient': the entity that undergoes an action or undergoes a change of state
- arg2: the 'beneficiary': the entity for whose benefit the action was performed


### SRL script

`srltest.py` creates a json file that we use for a D3 visualization of student responses. 
It follows the following procedure: 

1. Read the output of the AllenNLP Semantic Role Labeller for a set of our responses.
2. Perform co-reference resolution on the full sentences. 
3. Identify the main verb in the responses, using a few simple rules.
4. Group every response first by arg0 (mostly the subject), and then by main verb, combining
the results of the Semantic Role Labelling and co-reference resolution.
5. Use one of our topic classifiers to predict the topic. 
6. Output the tree to a json file.


