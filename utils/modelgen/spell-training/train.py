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

API_URL = "http://127.0.0.1:5000" # Currently set to localhost
JOB_ID = 139
JOB_URL = API_URL + '/' + str(JOB_ID)

# Returns list of labeled_vectors from API, each training_example is (deflated_vector, label)
# Returned object is in format: [({5:1, 6:2, 5000:1}, 1), ...]
# TODO: Set up pagination using offset and limit here. Will pass as params in the request.
def get_labeled_vectors(offset, limit):
    payload = {'offset': offset, 'limit': limit, 'full_info': 0}
    r = requests.get(url=JOB_URL, params=payload)
    examples_json = r.json()['labeled_vector']
    return [(example['vector'], example['label']) for example in examples_json]

def get_model_info():
    payload = {'offset': 0, 'limit': 0, 'full_info': 1}
    r = requests.get(url=JOB_URL, params=payload)
    info_json = r.json()
    return info_json['input_vector_length'], info_json['num_classes'], info_json['num_examples']

# Given a deflated_vector (dictionary), return its vector (sparse np array)
def inflate(deflated_vec, vec_len):
    result = np.zeros(vec_len)
    for idx, count in deflated_vec.items():
        result[int(idx)] = count
    return result


# Building, training TF Model ##################################################

# Builds the model, given proper parameters
def build_model(input_vec_length, num_classes):
    tf.reset_default_graph() # This resets all parameters and variables, leave this here
    net = tflearn.input_data([None, input_vec_length])                # Input
    net = tflearn.fully_connected(net, 10, activation='ReLU')     # Hidden
    net = tflearn.fully_connected(net, num_classes, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)
    return model


# Trains model in successive slabs by pulling slabs of data from the API
def train_model(model, num_classes, slab_size, save_file):
    print("Training TF model...")
    _, _, num_examples = get_model_info()
    start_pos = 0
    while start_pos < num_examples:
        end_pos = min(start_pos + slab_size, num_examples)
        examples = get_labeled_vectors(start_pos, slab_size)
        print('Fitting model with start: {}, end: {}'.format(start_pos, end_pos))
        x_train = np.asarray([inflate(vec['indices'], vec['reductions']) for vec, _ in examples])
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
    return model

SAVE_FILE = 'test-model.tfl'
INPUT_VEC_LEN, NUM_CLASSES, _ = get_model_info()
print("Building Tensorflow model...")
model = build_model(input_vec_length=INPUT_VEC_LEN, num_classes=NUM_CLASSES)
model = train_model(model, NUM_CLASSES, slab_size=30000, save_file=SAVE_FILE)
