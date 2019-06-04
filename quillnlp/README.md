# QuillNLP

This package contains the main code for Quill's NLP capabilities. 
This includes the dataset readers, models and predictors that we use
in our AllenNLP experiments.

## Run AllenNLP Experiments

This section explains how to run a simple experiment with AllenNLP. 

### 1. Training

In the first part of the experiment, we train a model. This is done with the command
`allennlp train`. The first argument to this command is an experiment configuration file,
which we store in the `experiments/` directory. This configuration file tells AllenNLP how
it should read and preprocess the data, what model it should use, and how this model should 
be trained. Because we use our own custom dataset readers and models, it is important to 
include the `quillnlp` package with `--include-package quillnlp`. We also tell AllenNLP
where it should store the results with `-s /tmp/junkfood_because/`.

`> allennlp train experiments/junkfood_because_topic_classifier_cpu.json -s /tmp/junkfood_because/ --include-package quillnlp`

### 2. Prediction

Second, we can use the trained model to make predictions for new data. This is done with 
the `allennlp predict` command. The first argument to this command is a model file that
was saved during the training process above. The second is an ndjson file with the texts
this model should analyze. Like above, we also point AllenNLP to our own `quillnlp` package,
which defines our custom dataset readers, models and predictors.

`> allennlp predict /tmp/junkfood_because/model.tar.gz data/interim/junkfood_because_test.ndjson --include-package quillnlp --predictor topic_classifier`

### 3. Evaluation

Third, we need to evaluate the quality of our model. We do this in one of two ways:

#### 3.1 AllenNLP evaluation

AllenNLP has an inbuilt evaluation procedure, which can be run using `allennlp evaluate`. 
The arguments to this command are the same as in the prediction step above. At the end of
the evaluation procedure, it will print out an overall performance score for the model.

`> allennlp evaluate /tmp/junkfood_but_coref/model.tar.gz data/interim/junkfood_but_test.ndjson --include-package quillnlp`

#### 3.2 Custom evaluation

For a rigorous evaluation of our models, we'd like to get more detailed results than
AllenNLP offers. We therefore have our own evaluation scripts. These can be run 
with the test data and the model as arguments, for example:

`python scripts/evaluate_topic_classification.py data/interim/junkfood_because_test.ndjson /tmp/junkfood_because/model.tar.gz`

### 4. Demo

Finally, it's easy to run a simple web demo with the model in the background. In this 
web demo, you can enter new text and see the predictions of the model. 

This is the example command for one of our classifiers: 

`> python -m allennlp.service.server_simple --archive-path /tmp/junkfood_because/model.tar.gz --field-name text --port 8234 --predictor topic_classifier --include-package quillnlp`