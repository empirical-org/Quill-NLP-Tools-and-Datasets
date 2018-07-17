"""Template for pulling training examples from API and training model on GPU"""
print("loading libraries...")
import json
import requests
import numpy as np
import tensorflow as tf
import tflearn
from tflearn.data_utils import to_categorical
import gc

# Fetching data from API #######################################################

api_url = "http://127.0.0.1:5000" # Currently set to localhost

# Returns list of training_examples from API, each training_example is (pre_vector, label)
# Returned object is in format: [({5:1, 6:2, 5000:1}, 1), ...]
# TODO: Set up pagination using offset and limit here. Will pass as params in the request.
def get_training_examples(offset, limit):
    r = requests.get(url=api_url)
    examples_json = r.json()['training_examples']
    return [(example['pre_vector'], example['label']) for example in examples_json]

# Returns the length of vectors for our training examples
def get_input_vector_length():
    r = requests.get(api_url + "/input_vector_length")
    return r.json()['input_vector_length']

# Returns the number of classes we are trying to distinguish between
def get_num_classes():
    r = requests.get(api_url + "/num_classes")
    return r.json()['num_classes']

# Returns the number of training examples in database
def get_num_examples():
    r = requests.get(api_url + "/num_examples")
    return r.json()['num_examples']

# Given a pre_vector (dictionary), return its vector (sparse np array)
def inflate(pre_vector, vec_len):
    result = np.zeros(vec_len)
    for idx, count in pre_vector.items():
        result[int(idx)] = count
    return result


# Building, training TF Model ##################################################

# Builds the model, given proper parameters
def build_model(input_vec_length, num_classes):
    tf.reset_default_graph() # This resets all parameters and variables, leave this here
    net = tflearn.input_data([None, input_vec_length])                # Input
    net = tflearn.fully_connected(net, 200, activation='ReLU')    # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')     # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)
    return model


# Trains model in successive slabs by pulling slabs of data from the API
def train_model(model, input_vec_length, num_classes, slab_size, save_file):
    print("Training TF model...")
    num_examples = get_num_examples()
    start_pos = 0
    while start_pos < num_examples:
        end_pos = min(start_pos + slab_size, num_examples)
        examples = get_training_examples(start_pos, slab_size)
        print('Fitting model with start: {}, end: {}'.format(start_pos, end_pos))
        x_train = np.asarray([inflate(pre_vec, input_vec_length) for pre_vec, _ in examples])
        y_train = to_categorical(np.asarray([lab for _, lab in examples]), num_classes)
        model.fit(x_train, y_train, validation_set=0.1, show_metric=True, batch_size=128, n_epoch=5)

        del examples
        gc.collect() # force Garbage Collector to release unreferenced memory

        start_pos = end_pos
        if (end_pos/slab_size) % 20 == 0: # save a copy of the model every 20 slabs
            print('Saving model in current state... still training.')
            model.save(save_file)

    print("Saving model...(final save)")
    model.save(save_file)
    print('-----')
    print('Success! Your model was built and saved.')


INPUT_VEC_LEN = get_input_vector_length()
NUM_CLASSES = get_num_classes()
print("Building Tensorflow model...")
model = build_model(input_vec_length=INPUT_VEC_LEN, num_classes=NUM_CLASSES)
train_model(model, INPUT_VEC_LEN, NUM_CLASSES, slab_size=10000, save_file='test-model.tfl')
