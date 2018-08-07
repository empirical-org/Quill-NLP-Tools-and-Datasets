from flask import Flask, request, render_template, jsonify
from shutil import copyfile
from tabulate import tabulate
from uuid import uuid4
import csv
import json
from git import Repo
import logging
from pathlib import Path
import os
import psycopg2
import requests
import shlex
import socket
import subprocess
import tarfile
import threading
import time
import yaml

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='nlpjobmanagerapi_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/nlpjobmanagerapilogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.DEBUG) # Changed by Eric Aug. 1
logger = logging.getLogger('nlpjobmanagerapi')


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

def cast_spell(job_id):
        # get hash for job if job exists
        cur.execute('SELECT name,hash FROM jobs WHERE id=%s', (job_id,))
        job_name, job_hash = cur.fetchone()
        # create working directory
        jobs_dir = '/var/lib/jobs'
        working_dir = '{}/{}'.format(
                jobs_dir, job_name)
        train_dir = '{}/train'.format(working_dir)
        create_working_dir = 'mkdir -p {}'.format(working_dir)
        subprocess.call(shlex.split(create_working_dir))
        # see if directory is locked, if it is, suggest trying later
        if os.path.isfile('{}/locked'.format(working_dir)): # non-zero code
            raise Exception('Another job has locked the directory, try again'
            'later.  If the error persists, talk to the system admin.')
        # checkout hash and extract important files to temp location
        os.chdir(jobs_dir)
        if not os.path.isdir('{}/.git'.format(working_dir)):
            os.chdir(jobs_dir)
            Repo.clone_from(repo_url, job_name)
        os.chdir(working_dir)
        ro = Repo(working_dir)
        ro.remotes.origin.fetch()
        # checkout commit version
        ro.git.checkout(job_hash)
        # lock directory
        Path('{}/locked'.format(working_dir)).touch()
        # change to training dir
        os.chdir(train_dir)
        # create virtualenv if non existent
        subprocess.call(shlex.split('virtualenv -p python3 venv'))
        # install dependencies
        subprocess.call(shlex.split('pip install -r requirements.txt'))
        # cast spell (non blocking, faster return)
        os.environ['JOB_ID'] = str(job_id)
        subprocess.Popen(shlex.split('./venv/bin/python castspell.py'))
        # unlock
        os.remove('{}/locked'.format(working_dir))
        # 202, initiated # 202 accepted, asyc http code
        return True


def become_wizard(unique_id, job_id):

    # Check if another droplet has already claimed the defense against the dark
    # arts post. if so exit, if not mark that one is running then continue.
    cur.execute("""UPDATE jobs SET meta=jsonb_set(meta, '{wizard}', %s), updated=DEFAULT
                    WHERE NOT(meta ? 'wizard')
                    AND id=%s
                """, (json.dumps(unique_id),job_id))
    conn.commit()
    cur.execute("""SELECT COUNT(*) FROM jobs WHERE
                    meta->'wizard'=%s 
                    AND id=%s
                """,
            (json.dumps(unique_id), job_id))
    return cur.fetchone()[0] == 1

def set_droplet_names(job_description):
    num_names = job_description['job']['droplet_count']
    job_name = job_description['job']['name']
    if job_description['droplet'].get('names') == 'autogenerate':
        names = [job_name + str(n) for n in range(num_names)] 
        job_description['droplet']['names'] = names
    return job_description


def create_droplets(description, job_id, droplet_objects):
    create_droplets_url = "https://api.digitalocean.com/v2/droplets"
    payload = description['droplet'] 
    # set names for droplet / droplets 
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    headers['Content-Type'] = 'application/json'
    r = requests.post(create_droplets_url, json=payload, headers=headers)
    logger.info('DO request response:')
    logger.info(r.json())
    # blow up now if the droplet wasn't created
    r.raise_for_status()

    # get droplet uids 
    if description['droplet'].get('names'):
        droplet_uids = [drop['id'] for drop in r.json()['droplets']]
    else:
        droplet_uids = [r.json()['droplet']['id']]

    # update status, set uid for droplets in database
    for i, droplet_obj in enumerate(droplet_objects):
        droplet_obj['uid'] = i

    # replace the droplet objects with the new ones that include uid
    logger.debug('add uid to droplets {}'.format(i))
    cur.execute("UPDATE nlpjobs SET data = jsonb_set(data, '{droplets}', %s) WHERE id=%s",
        (json.dumps(droplet_objects), job_id))
    conn.commit()
    # update job state
    cur.execute("UPDATE nlpjobs SET data = jsonb_set(data, '{state}', '\"droplets-created\"') WHERE id=%s",
        (job_id,))
    conn.commit()

    # update job state
    set_job_state(job_id, 'droplets-created')

    return droplet_objects


def wait_for_droplet_to_be_created(droplet_obj):
    droplet_uid = droplet_obj['uid']
    check_droplet_url = "https://api.digitalocean.com/v2/droplets/{}"
    check_droplet_url = check_droplet_url.format(droplet_uid)
    status = ''
    while status != 'active':
        time.sleep(3) # no need to check this incessently
        headers = {}
        headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
        r = requests.get(check_droplet_url, headers=headers)
        drop = r.json()['droplet']
        status = drop['status']
        logger.debug('waiting for droplet with uid {}.  current status {}'.format(
            droplet_uid, status))

    droplet_obj['memory'] = drop['memory']
    droplet_obj['vcpus'] = drop['vcpus']
    droplet_obj['disk'] = drop['disk']
    droplet_obj['locked'] = drop['locked']
    droplet_obj['created_at'] = drop['created_at']
    droplet_obj['status'] = drop['status']
    droplet_obj['backup_ids'] = drop['backup_ids']
    droplet_obj['snapshot_ids'] = drop['snapshot_ids']
    droplet_obj['features'] = drop['features']
    droplet_obj['region'] = drop['region']
    droplet_obj['image'] = drop['image']
    droplet_obj['size'] = drop['size']
    droplet_obj['size_slug'] = drop['size_slug']
    droplet_obj['networks'] = drop['networks']
    droplet_obj['kernel'] = drop['kernel']
    droplet_obj['next_backup_window'] = drop['next_backup_window']
    droplet_obj['tags'] = drop['tags']
    droplet_obj['volume_ids'] = drop['volume_ids']
    return droplet_obj

def initizialize_job_in_database(job_name, commit_hash):
    job_obj = json.dumps({'hash':commit_hash, 'name':job_name})
    cur.execute("INSERT INTO nlpjobs (data) VALUES (%s) RETURNING id", (job_obj,))
    return cur.fetchone()[0]

def initizialize_droplets_in_database(job_description, job_name, job_id):
    droplet_objects = []
    if job_description['droplet'].get('names'):
        for i, droplet_name in enumerate(job_description['droplet']['names']):
            droplet_objects.append({'name': droplet_name})
    else:
        droplet_name = job_description['droplet']['name']
        droplet_objects.append({'name': droplet_name})
    cur.execute("UPDATE nlpjobs SET data = jsonb_set(data, '{droplets}', %s) WHERE id=%s",
            (json.dumps(droplet_objects), job_id))
    conn.commit()
    return droplet_objects
    

    droplet_ids = []
    if job_description['droplet'].get('names'):

        for droplet_name in job_description['droplet']['names']:
            cur.execute("INSERT INTO droplets (name, job_id) values (%s, %s)",
                    (droplet_name, job_id))
            conn.commit()
            cur.execute("SELECT id FROM droplets WHERE name = %s",
                    (droplet_name,))
            droplet_ids.append(cur.fetchone()[0])
    else:
        droplet_name = job_description['droplet']['name']
        cur.execute("INSERT INTO droplets (name, job_id) values (%s, %s)",
                (droplet_name, job_id))
        conn.commit()
        cur.execute("SELECT id FROM droplets WHERE name = %s",
                (droplet_name,))
        droplet_ids.append(cur.fetchone()[0])
    return droplet_ids

def update_active_droplets(droplet_objects, job_id):
    cur.execute("UPDATE nlpjobs SET data = jsonb_set(data, '{droplets}', %s) WHERE id=%s",
        (json.dumps(droplet_objects), job_id))
    conn.commit()


def set_job_state(job_id, state):
    cur.execute("UPDATE nlpjobs SET data = jsonb_set(data, '{state}', %s) WHERE id=%s",
        (json.dumps(state), job_id))
    conn.commit()


def run_job(job_description, job_id, job_name, 
        playbook_fname, job_hash, working_dir, repo):
    try:
        # initialize droplets in database
        logger.info("initializing droplets in database")
        droplet_objects = initizialize_droplets_in_database(job_description, job_name, job_id)

        # create droplet or droplets (job.state droplets-created)
        logger.info("creating droplet(s)")
        droplet_objects = create_droplets(job_description, job_id, droplet_objects)

        # wait for droplets to be created (updates droplet status and all
        # other fields )
        logger.info("waiting for droplets to be created")
        new_droplet_objects = []
        for droplet_obj in droplet_objects:
            new_droplet_objects.append(wait_for_droplet_to_be_created(droplet_obj))
        droplet_objects = new_droplet_objects
        update_active_droplets(droplet_objects, job_id)

        # (job.state droplets-active)
        set_job_state(job_id, 'droplets-active')
        
        # wait a minute to make sure all droplets are really online + responsive
        time.sleep(60)

        # run ansible on the droplets to install dependencies, job bundle,
        # set environment variables, create ssh tunnels, start jobs 
        logger.info("installing dependencies and starting jobs on remote droplet(s)")
        hosts_string = ','.join([str(d_uid) for d_uid in droplet_uids])
        ansible_command = 'ansible-playbook {} -i \
                /etc/ansible/digital_ocean.py -e \
                hosts_string={} -e job_id={} -e job_name={} \
                -e job_hash={} -e repo={}'.format(
                        playbook_fname, hosts_string, job_id, job_name,
                        job_hash, repo)
        logger.info(ansible_command)
        # subprocess.call is blocking, and this is IMPORTANT.
        # if we switch to Popen, make sure the call is blocking.
        ansiblelogfile = '/var/log/playbooklogs/{}_ansible.log'.format(job_id)
        with open(ansiblelogfile) as logf:
            subprocess.call(shlex.split(ansible_command),
                    stdout=logf,stderr=subprocess.STDOUT)
        logger.info("droplets working, job {}-{} started successfully".format(
            job_name, job_id))
        logger.info('removing lock file created for this job...')
        os.remove('{}/locked'.format(working_dir))
    except psycopg2.Error as e:
        ref = 'https://www.postgresql.org/docs/current/static/errcodes-appendix.html'
        logger.error('pgcode {}'.format(e.pgcode) + ref)


@app.route('/')
def man():
    return jsonify('The api is running.')


@app.route('/jobs', methods=["GET", "POST"])
def jobs():
    if request.method == "GET":
        return jsonify("Method not available")
    elif request.method == "POST":
        try:
            # gather information to create job
            job_name = request.form['job']
            job_hash = request.form['hash']
            repo_url = request.form['repo']

            # 
            jobs_dir = '/var/lib/jobs'
            working_dir = '{}/{}'.format(
                    jobs_dir, job_name)

            # initialize job in database (job.state, initialized)
            job_id = initizialize_job_in_database(job_name, job_hash)

            # create working directory
            create_working_dir = 'mkdir -p {}'.format(working_dir)
            subprocess.call(shlex.split(create_working_dir))

            
            # see if directory is locked, if it is, suggest trying later
            if os.path.isfile('{}/locked'.format(working_dir)): # non-zero code
                raise Exception('Another job has locked the directory, try again'
                'later.  If the error persists, talk to the system admin.')

            # checkout hash and extract important files to temp location
            os.chdir(jobs_dir)
            if not os.path.isdir('{}/.git'.format(working_dir)):
                os.chdir(jobs_dir)
                Repo.clone_from(repo_url, job_name)
            os.chdir(working_dir)
            ro = Repo(working_dir)
            ro.remotes.origin.fetch()
            ro.git.checkout(job_hash)

            Path('{}/locked'.format(working_dir)).touch()

            # make job description dictionary
            jd_fname = '{}/description.yml'.format(working_dir)
            with open(jd_fname, 'r') as jdf:
                job_description = yaml.load(jdf)
            job_description = set_droplet_names(job_description)

            playbook_fname = '{}/playbook.yml'.format(working_dir)

            # run job
            thr = threading.Thread(target=run_job, args=(job_description,
                job_id, job_name, playbook_fname,
                job_hash, working_dir, repo_url), kwargs={})
            thr.start() # Will run "post_job"
            if thr.is_alive():
                return jsonify('Job initialized. Working.'), 202 # 202 accepted, asyc http code
            return jsonify('Unexpected error. Please check with sys admin', 500)
        except KeyError as e:
            return jsonify({'error':'supply form param job w job name'}), 400
        except tarfile.TarError as e:
            return jsonify({'error':'job doesnt exist or improperly formatted'}), 400
        except psycopg2.Error as e:
            conn.rollback()
            ref = 'https://www.postgresql.org/docs/current/static/errcodes-appendix.html'
            return jsonify({'error':'pgcode {} ({})'.format(e.pgcode, ref)}), 400
        except Exception as e:
            return jsonify({'error':str(e)}), 555


@app.route('/jobs/<job_id>/state', methods=["GET"])
def get_job_status(job_id):
    try:
        cur.execute("SELECT data->>'state' FROM jobs WHERE id=%s", (job_id,))
        return jsonify(cur.fetchone()[0]), 200
    except (IndexError, psycopg2.Error) as e:
        return jsonify('error'), 404


@app.route('/jobs/<int:job_id>/spell', methods=["POST"])
def try_to_cast_spell(job_id):
    try:
        i_got_my_letter = become_wizard(str(uuid4()), job_id)
        if i_got_my_letter:
            thr = threading.Thread(target=cast_spell, args=(job_id,
                ), kwargs={})
            thr.start() # Will run "post_job"
            if thr.is_alive():
                return jsonify('Spell training session launched for job.'), 202
        else:
            return jsonify("You're a muggle harry."), 423

    except Exception as e:
        return jsonify({'error':str(e)}), 400 


@app.route('/droplets/<droplet_uid>', methods=["DELETE"])
def individual_droplet(droplet_uid):
    logger.info('attempting to delete droplet with uid {}'.format(droplet_obj))
    # send delete request to D.O api
    delete_droplets_url = "https://api.digitalocean.com/v2/droplets/{}".format(
            droplet_uid)
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    r = requests.delete(delete_droplets_url, headers=headers)
    return '', r.status_code


@app.route('/jobs/<int:job_id>/vectors')
def training_data(job_id):
    '''Returns training_examples for a given job_id from offset to limit
    If full_info parameter is greater than 0, will return extra architecture
    info,
    GET /jobs/139/vectors?offset=0&limit=10&full_info=1
    {
    "labeled_vectors": [{"vector":{"indices": {"0": 1}, "reductions": 3}, "label":0},
                        {"vector":{"indices": {"1": 1}, "reductions": 3}, "label":1},
                        ...],
    "vector_length": 3, # non-negative int or -1 if vector length is inconsistent
    "num_labeled_vectors": 1600000, # non-negative int
    "num_classes": 2, # pos integer, probably 2 or more
    }
    '''
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 0)
    cur.execute('SELECT vector,label FROM vectors WHERE job_id=%s OFFSET %s LIMIT %s',
            (job_id, offset, limit))
    training_examples = [{'vector':v,'label':l} for v,l in cur]
    data = { 'labeled_vectors': training_examples }

    if int(request.args.get('full_info', 0)) > 0:
        cur.execute("SELECT vector->>'reductions' AS num_reductions FROM vectors WHERE job_id=%s GROUP BY num_reductions",
                (job_id,))
        unique_num_reductions = cur.fetchall() # [[5000]]
        if len(unique_num_reductions) > 1:
            # the vector length for this job is inconsistent! set vector_length
            # to -1
            data['vector_length'] = -1
        else:
            data['vector_length'] = unique_num_reductions[0][0]

        cur.execute("SELECT count(*) FROM vectors WHERE job_id=%s",
                (job_id,))
        data['num_labeled_vectors'] = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM (SELECT label FROM vectors WHERE job_id=%s GROUP BY label) AS all_vecs_for_job",
                (job_id,))
        data['num_classes'] = cur.fetchone()[0]

    return jsonify(data)


if __name__ == '__main__':
    app.run(port=10600, host='0.0.0.0', debug=True)
