from flask import Flask
from flask import jsonify
import psycopg2
app = Flask(__name__)

# Database access constants
# DB_PASSWORD = os.environ.get('SVA_PASSWORD', '')
DB_NAME = 'quill_aed_test'
DB_USER = 'etang'
DB_PORT = '5432'
DB_HOST = 'localhost'

# Connect to database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, port=DB_PORT, host=DB_HOST)
cur = conn.cursor()

# Returns the training data
# TODO: Populate using DB data instead of hardcoding
@app.route('/')
def training_data():
    # pre_vector is dict. of index:count that can be reconstructed into a vector
    # num_reductions is the dimension of that vector
    data = {
        'training_examples': [
            {'pre_vector': {5:1, 6:2, 500:1}, 'label': 1},
            {'pre_vector': {5:1, 2000:1}, 'label': 0}
        ],
        'vector_length': 5000
    }
    return jsonify(data)

# Returns length of each input vector
# TODO: Populate using DB data instead of hardcoding
@app.route('/input_vector_length')
def input_vector_length():
    data = {
        'input_vector_length': 5000
    }
    return jsonify(data)

# Returns number of classes we are classifying
# TODO: Populate using DB data instead of hardcoding
@app.route('/num_classes')
def num_classes():
    data = {
        'num_classes': 2
    }
    return jsonify(data)

# Returns the number of total examples
# TODO: Populate using DB data instead of hardcoding
@app.route('/num_examples')
def num_examples():
    data = {
        'num_examples': 2
    }
    return jsonify(data)
