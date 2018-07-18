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
# If full_info parameter is greater than 0, will return extra architecture info
@app.route('/<int:job_id>')
def training_data(job_id):
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 0)
    cur.execute('SELECT vector,label FROM vectors WHERE job_id=%s OFFSET %s LIMIT %s', (job_id, offset, limit))
    training_examples = [(v,l) for v,l in cur]
    data = { 'training_examples': training_examples }

    if int(request.args.get('full_info', 0)) > 0:
        cur.execute('SELECT label FROM vectors WHERE job_id=%s', (job_id, ))
        all_labels = [int(l[0]) for l in cur]
        data['num_classes'] = max(all_labels, default=-1) + 1
        data['num_examples'] = len(all_labels)

        cur.execute('SELECT vector FROM vectors WHERE job_id=%s LIMIT 1', (job_id, ))
        first_vec = cur.fetchone()
        data['input_vector_length'] = 0 if (first_vec is None) else first_vec[0]['reductions']

    return jsonify(data)

# An endpoint solely for testing, returns all vectors in table
@app.route('/all_vectors')
def all_vectors():
    cur.execute('SELECT * FROM vectors')
    data = {
        'all_vectors': [x for x in cur]
    }
    return jsonify(data)
