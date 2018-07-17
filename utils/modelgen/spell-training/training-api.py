from flask import Flask
from flask import jsonify
from flask import request
import psycopg2
import os
import json
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

# Returns training_examples for a given job_id from offset to limit
@app.route('/<int:job_id>')
def training_data(job_id):
    offset = request.args.get('offset', None)
    limit = request.args.get('limit', None)
    cur.execute('SELECT vector,label FROM vectors WHERE job_id=%s OFFSET %s LIMIT %s', (job_id, offset, limit))
    training_examples = [(v,l) for v,l in cur]

    cur.execute('SELECT count(*) FROM vectors WHERE job_id=%s', (job_id, ))
    num_examples = cur.fetchone()[0]

    data = {
        'training_examples': training_examples,
        'num_examples': num_examples
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

# An endpoint solely for testing, returns all vectors in table
@app.route('/all_vectors')
def all_vectors():
    cur.execute('SELECT * FROM vectors')
    data = {
        'all_vectors': [x for x in cur]
    }
    return jsonify(data)
