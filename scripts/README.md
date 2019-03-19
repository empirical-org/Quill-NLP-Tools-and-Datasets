This directory contains scripts for testing NLP functionality.

## Semantic Role Labelling

Semantic role labelling identifies the verbs in a sentence and the semantic roles that are associated with them.
These roles are:

- arg0: the 'agent': the entity that initiates an action
- arg1: the 'patient': the entity that undergoes an action or undergoes a change of state
- arg2: the 'beneficiary': the entity for whose benefit the action was performed

`srltest.py` applies the AllenNLP semantic role labelling model to a set of example responses about junk food
and post-processes the results.