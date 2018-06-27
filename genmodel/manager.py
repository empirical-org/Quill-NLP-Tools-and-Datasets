from flask import Flask, request, render_template, jsonify
from tabulate import tabulate
import os
import psycopg2
import requests
import yaml

# Connect to Database
try:
    DB_NAME=os.environ['DB_NAME']
    DB_USER=os.environ['DB_USER']
    DB_PASS=os.environ['DB_PASS']
except KeyError as e:
    raise Exception('environment variables for database connection must be set')

conn = psycopg2.connect(dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host='localhost',
        port=5432
    )



app = Flask(__name__)


@app.route('/')
def man():
    return 'Not implemented'

@app.route('/jobs', methods=["GET", "POST"])
def jobs():
    if request.method == "GET":
        cur = conn.cursor()
        cur.execute("SELECT id,name,state,created FROM jobs WHERE state='running'")
        resp_list = cur.fetchall()
        cur.close()
        return tabulate(resp_list, headers=['id','name','state','created'])
    elif request.method == "POST":
        create_droplet_url = "https://api.digitalocean.com/v2/droplets"
        req = yaml.load(request.files['job'])
        payload = req['job']['droplet']
        headers = {}
        headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
        headers['Content-Type'] = 'application/json'
        r = requests.post(create_droplet_url, json=payload, headers=headers)
        return jsonify(r.json()), 201
    else:
        return 'Not implemented'


@app.route('/jobs/<job_id>', methods=["GET", "PATCH", "DELETE"])
def job_for_id(job_id):
    if request.method == "GET":
        # Job monitoring for a specific job
        return 'GET job #' + job_id
    elif request.method == "PATCH":
        # TODO: Should this be an endpoint?
        # Modify job, scale resolvers
        return 'PATCH job #' + job_id
    elif request.method == "DELETE":
        # Remove all dedicated Digital Ocean containers, stop all publishers,
        # writers and workers. Purge the queue.
        return 'DELETE job #' + job_id
    return job_id


if __name__ == '__main__':
    app.run(port=5000, host= '0.0.0.0', debug=True)
