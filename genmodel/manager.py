from flask import Flask, request, render_template, jsonify
from tabulate import tabulate
from uuid import uuid4
import os
import psycopg2
import requests
import subprocess
import tarfile
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
cur = conn.cursor()



app = Flask(__name__)


def set_droplet_names(job_description):
    num_names = job_description['job']['droplet_count']
    job_name = job_description['job']['name']
    if job_description['droplet'].get('names') == 'autogenerate':
        names = [job_name + n for n in range(num_names)] 
        job_description['droplet']['names'] = names
    return job_description


def create_droplets(description={}):
    create_droplets_url = "https://api.digitalocean.com/v2/droplets"
    payload = description['droplet'] 
    # set names for droplet / droplets 
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    headers['Content-Type'] = 'application/json'
    r = requests.post(create_droplets_url, json=payload, headers=headers)

    # get droplet uids 
    if description['droplet'].get('names'):
        droplet_uids = [drop['id'] for drop in r.json()['droplets']]
    else:
        droplet_uids = [r.json()['droplet']['id']]

    # update state, set uid for droplets in database
    for uid in droplet_uids:
        cur.execute("UPDATE droplets SET uid=?, state='created'", (uid,))

    return droplet_uids


def wait_for_droplet_to_be_created(droplet_uid):
    check_droplet_url = "https://api.digitalocean.com/v2/droplets/{}"
    check_droplet_url = check_droplet_url.format(droplet_uid)
    status = ''
    while status != 'active':
        time.sleep(8) # no need to check this incessently
        r = requests.get(check_droplet_url, headers=headers)
        drop = r.json()['droplet']
        status = drop['status']

    # update droplet status, and set other attrs
    cur.execute("""UPDATE droplets 
                SET status='active',
                    memory=?,	
                    vcpus=?,
                    disk=?,
                    locked=?,
                    created_at=?,
                    status=?,
                    backup_ids=?,
                    snapshot_ids=?,
                    features=?,
                    region=?,
                    image=?,
                    size=?,
                    size_slug=?,
                    networks=?,
                    kernel=?,
                    next_backup_window=?,
                    tags=?,
                    volume_ids=?
                WHERE uid=?
                """, (uid, drop['memory'], drop['vcpus'], drop['disk'],
                    drop['locked'], drop['created_at'], drop['status'],
                    drop['backup_ids'], drop['snapshot_ids'], drop['features'],
                    drop['region'], drop['image'], drop['size'],
                    drop['size_slug'], drop['networks'], drop['kernel'],
                    drop['next_backup_window'], drop['tags'],
                    drop['volume_ids'])
                )
    conn.commit()
    return status


def initizialize_job_in_database(job_name):
    cur.execute("INSERT INTO jobs (name,state) values (?, ?)",
            (job_name, 'initialized'))
    conn.commit()
    cur.execute('SELECT id FROM jobs WHERE name = ?', (job_name,))
    return cur.fetchone()[0]


def initizialize_droplets_in_database(job_description, job_name, job_id):
    droplet_ids = []
    if job_description['droplet'].get('names'):
        for droplet_name in job_description['droplet']['names']:
            cur.execute("INSERT INTO droplets (name, job_id) values (?, ?)",
                    (droplet_name, job_id))
            conn.commit()
            cur.execute("SELECT id FROM droplets WHERE name = ?",
                    (droplet_name,))
            droplet_ids.append(cur.fetchone()[0])
    else:
        droplet_name = job_description['droplet']['name']
        cur.execute("INSERT INTO droplets (name, job_id) values (?, ?)",
                (droplet_name, job_id))
        conn.commit()
        cur.execute("SELECT id FROM droplets WHERE name = ?",
                (droplet_name,))
        droplet_ids.append(cur.fetchone()[0])
    return droplet_ids

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
        try:
            # gather information to create job
            job_name = request.form['job']
            with tarfile.open('/root/jobs/{}.tar.gz'.format(job_name)) as tar:
                # make job description dictionary
                jd_fname = '{}/description.yml'.format(job_name)
                job_description = tar.extractfile(jd_fname)
                job_description = yaml.load(description=job_description)
                job_description = set_droplet_names(job_description)
                # save playbook to temporary local file
                zipped_playbook_fname = '{}/playbook.yml'.format(job_name)
                playbook = tar.extractfile(zipped_playbook_fname)
                playbook_fname = 'playbook_{}.yml'.format(str(uuid4())[:8])
                with open(playbook_fname, 'w') as pb:
                    pb.write(playbook.read())

            # initialize job in database
            job_id = initizialize_job_in_database(job_name)
            # initialize droplets in database
            droplet_ids = initizialize_droplets_in_database(job_description, job_name, job_id)

            # create droplet or droplets (updates droplet state, uid)
            droplet_uids = create_droplets(description=job_description)

            # wait for droplets to be created (updates droplet state and all
            # other fields )
            for droplet_id in droplet_ids:
                status = wait_for_droplet_to_be_created(droplet_id)
            
            # wait 10s to make sure all droplets are really online + responsive
            time.sleep(10)

            # run ansible on the droplets to install dependencies, job bundle,
            # set environment variables, create ssh tunnels, start jobs
            hosts_string = ':'.join(droplet_ids)
            ansible_command = 'ansible-playbook {} -i \
                    /etc/ansible/digital_ocean.py --list-hosts -e \
                    do_ids={}'.format(playbook_fname, hosts_string)
            output = subprocess.check_output(['bash','-c', ansible_command])

            # - add the job to the master database
            # - start blah blah, finish this tm
            return jsonify(r.json()), 202 # 202 accepted, asyc http code
        except KeyError as e:
            return jsonify({'error':'supply form param job w job name'}), 400
        except tarfile.TarError as e:
            return jsonify({'error':'job doesnt exist or improperly formatted'}), 400
        except psycopg2.Error as e:
            ref = 'https://www.postgresql.org/docs/current/static/errcodes-appendix.html'
            return jsonify({'error':'pgcode {} ({})'.format(e.pgcode, ref)}), 400

    else:
        return 'Not implemented'

@app.route('/jobs/<job_id>/status', methods=["GET"])
def get_job_status(job_id):
    try:
        cur.execute('SELECT status FROM jobs WHERE job_id=?', (job_id,))
        return cur.fetchone()[0]
    except (IndexError, psycopg2.Error) as e:
        return jsonify({'error':'jobid does not exist'}), 404
    

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
