from flask import Flask
from flask import jsonify
import psycopg2
import os
app = Flask(__name__)

# Database access constants
DB_PASSWORD = os.environ.get('DB_PASS', '')
DB_NAME = os.environ.get('DB_NAME', '')
DB_USER = os.environ.get('DB_USER', DB_NAME)
DB_PORT = int(os.environ.get('DB_PORT', '54322'))
DB_HOST = 'localhost'

# Connect to database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, host=DB_HOST)
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
    cur.execute('SELECT vector FROM vectors LIMIT 1')
    vector_len = json.loads(cur.fetchone()[0])['reductions']
    data = {
        'input_vector_length': vector_len
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
    cur.execute('SELECT count(*) FROM vectors')
    num_examples = cur.fetchone()[0]
    data = {
        'num_examples': num_examples
    }
    return jsonify(data)
