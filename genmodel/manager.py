from flask import Flask, request, render_template, jsonify
from tabulate import tabulate
from uuid import uuid4
import os
import psycopg2
import requests
import subprocess
import threading
import time
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


def set_droplet_names(job_description):
    num_names = job_description['job']['droplet_count']
    job_name = job_description['job']['name']
    if job_description['droplet'].get('names') == 'autogenerate':
        names = [job_name + n for n in range(num_names)] 
        job_description['names'] = names
    return job_description


def create_droplets(description={}):
    create_droplet_url = "https://api.digitalocean.com/v2/droplets"
    payload = description['droplet'] 
    # set names for droplet / droplets 
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    headers['Content-Type'] = 'application/json'
    r = requests.post(create_droplet_url, json=payload, headers=headers)
    droplet_id = r.json()['droplet']['id']
    return droplet_id


def wait_for_droplet_to_be_created(droplet_id):
    check_droplet_url = "https://api.digitalocean.com/v2/droplets/{}"
    check_droplet_url = check_droplet_url.format(droplet_id)
    status = ''
    while status != 'active':
        time.sleep(8) # no need to check this incessently
        r = requests.get(check_droplet_url, headers=headers)
        status = r.json()['droplet']['status']
    return status


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
        playbook = request.files['playbook']
        job_description = request.files['description']
        job_description = yaml.load(description=job_description)
        job_description = set_droplet_names(job_description)

        # create droplet
        droplet_id = create_droplet(description=job_description)

        # wait for droplet to be created
        status = wait_for_droplet_to_be_created(droplet_id)
        #ip_address = r1.json()['droplet']['networks']['v4'][0]['ip_address']

        # run ansible on the droplet to install dependencies, job bundle
        ansible_command = 'ansible-playbook {} -i /etc/ansible/digital_ocean.py --list-hosts -e do_id={}'.format(playbook, droplet_id)
        output = subprocess.check_output(['bash','-c', ansible_command])

        # - add the job to the master database
        # - start blah blah, finish this tm
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
