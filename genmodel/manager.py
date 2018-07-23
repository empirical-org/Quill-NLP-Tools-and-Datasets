from flask import Flask, request, render_template, jsonify
from shutil import copyfile
from tabulate import tabulate
from uuid import uuid4
import csv
import json
from git import Repo
import logging
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
    level=logging.INFO)
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


def set_droplet_names(job_description):
    num_names = job_description['job']['droplet_count']
    job_name = job_description['job']['name']
    if job_description['droplet'].get('names') == 'autogenerate':
        names = [job_name + str(n) for n in range(num_names)] 
        job_description['droplet']['names'] = names
    return job_description


def create_droplets(description, job_id, droplet_ids):
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

    # update status, set uid for droplets in database
    for i, droplet_id in enumerate(droplet_ids):
        logger.debug('updating droplet with id {}'.format(
            droplet_id))
        uid = droplet_uids[i]
        logger.debug('setting uid  to {} for droplet with id {}'.format(
            uid, droplet_id))
        cur.execute("""UPDATE droplets
                SET uid=%s, status='created', updated=DEFAULT
                WHERE id=%s""",
                (uid,droplet_id))
        conn.commit()

    # update job state to droplets-created 
    set_job_state(job_id, 'droplets-created')

    return droplet_uids


def wait_for_droplet_to_be_created(droplet_uid):
    check_droplet_url = "https://api.digitalocean.com/v2/droplets/{}"
    check_droplet_url = check_droplet_url.format(droplet_uid)
    status = ''
    while status != 'active':
        time.sleep(8) # no need to check this incessently
        headers = {}
        headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
        r = requests.get(check_droplet_url, headers=headers)
        drop = r.json()['droplet']
        status = drop['status']
        logger.debug('waiting for droplet with uid {}.  current status {}'.format(
            droplet_uid, status))

    try:
        # update droplet status, and set other attrs
        cur.execute("""UPDATE droplets 
                    SET memory=%s,	
                        vcpus=%s,
                        disk=%s,
                        locked=%s,
                        created_at=%s,
                        status=%s,
                        backup_ids=%s,
                        snapshot_ids=%s,
                        features=%s,
                        region=%s,
                        image=%s,
                        size=%s,
                        size_slug=%s,
                        networks=%s,
                        kernel=%s,
                        next_backup_window=%s,
                        tags=%s,
                        volume_ids=%s,
                        updated=DEFAULT
                    WHERE uid=%s
                    """, (drop['memory'], drop['vcpus'], drop['disk'],
                        drop['locked'], drop['created_at'], drop['status'],
                        drop['backup_ids'], drop['snapshot_ids'],
                        drop['features'], json.dumps(drop['region']),
                        json.dumps(drop['image']), json.dumps(drop['size']),
                        drop['size_slug'], json.dumps(drop['networks']),
                        json.dumps(drop['kernel']),
                        json.dumps(drop['next_backup_window']), drop['tags'],
                        drop['volume_ids'], droplet_uid)
                    )
        conn.commit()
    except psycopg2.Error as e:
        logger.error(e.pgerror)
        logger.error(str(e))
        raise(e)
    except Exception as e:
        logger.error(str(e))
        raise(e)
    return status


def initizialize_job_in_database(job_name, commit_hash):
    cur.execute("INSERT INTO jobs (name,state,meta, hash) values (%s, %s,'{}',%s)",
            (job_name, 'initialized', commit_hash))
    conn.commit()
    cur.execute('SELECT id FROM jobs WHERE hash = %s', (commit_hash,))
    return cur.fetchone()[0]


def initizialize_droplets_in_database(job_description, job_name, job_id):
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


def add_labeled_data_to_database(labeled_data_fname, job_id):
    try:
        with open(labeled_data_fname, 'r') as labeled_data_stream:
            # drop the job_id_idx for faster inserts
            cur.execute("DROP INDEX IF EXISTS job_id_idx")
            conn.commit()
            # insert data

            cur.copy_from(labeled_data_stream, 'labeled_data', columns=('data',
                'label', 'job_id'))
            conn.commit()

            # readd index
            cur.execute("CREATE INDEX IF NOT EXISTS job_id_idx ON labeled_data (job_id)")
            conn.commit()

            # update job state to loaded-data 
            set_job_state(job_id, 'loaded-data')
    except psycopg2.Error as e:
        conn.rollback()
        logger.error('there was an issue adding labeled data to the database')
        logger.error(e)
        raise e


def set_job_state(job_id, state):
    # update job state to loaded-data 
    cur.execute("""UPDATE jobs SET state=%s
                    WHERE id=%s
                """, (state,job_id))
    conn.commit()


def run_job(job_description, job_id, job_name, labeled_data_fname,
        playbook_fname, job_hash, working_dir, repo):
    try:
        logger.info("adding labeled data to database")
        # add labeled data to database (job.state, loaded-data)
        add_labeled_data_to_database(labeled_data_fname, job_id)

        # initialize droplets in database
        logger.info("initializing droplets in database")
        droplet_ids = initizialize_droplets_in_database(job_description, job_name, job_id)

        # create droplet or droplets (job.state droplets-created)
        logger.info("creating droplet(s)")
        droplet_uids = create_droplets(job_description, job_id, droplet_ids)

        # wait for droplets to be created (updates droplet status and all
        # other fields )
        logger.info("waiting for droplets to be created")
        for droplet_uid in droplet_uids:
            status = wait_for_droplet_to_be_created(droplet_uid)

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
        subprocess.call(shlex.split(ansible_command))
        logger.info("droplets working, job {}-{} started successfully".format(
            job_name, job_id))

        logger.info('removing lock file created for this job...')
        os.remove('{}/locked'.format(working_dir))
    except psycopg2.Error as e:
        ref = 'https://www.postgresql.org/docs/current/static/errcodes-appendix.html'
        logger.error('pgcode {}'.format(e.pgcode) + ref)


@app.route('/')
def man():
    with open('README.md') as f:
        return f.read()


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
            job_hash = request.form['hash']
            repo_url = request.form['repo']

            # 
            jobs_dir = '/var/lib/jobs'
            working_dir = '{}/{}'.format(
                    jobs_dir, job_name)
            labeled_data_location = '{}/labeled_data.csv'.format(
                    working_dir)
            labeled_data_db_format = '{}/ld.dbf'.format(
                    working_dir)

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


            pull_checkout_lock = 'git pull && git checkout {} && touch locked'.format(
                    job_hash)
            subprocess.call(shlex.split(pull_checkout_lock), shell=True)

            # move labeled data to file formatted for easy copy into postgres 
            with open(labeled_data_db_format, 'w') as ld:
                csvf = open(labeled_data_location, 'r')
                reader = csv.reader(csvf)
                for row in reader:
                    ld.write('{}\t{}\t{}\n'.format(row[0],row[1],job_id))
                ld.close()
                csvf.close()

            # make job description dictionary
            jd_fname = '{}/description.yml'.format(working_dir)
            with open(jd_fname, 'r') as jdf:
                job_description = yaml.load(jdf)
            job_description = set_droplet_names(job_description)

            playbook_fname = '{}/playbook.yml'.format(working_dir)

            # run job
            thr = threading.Thread(target=run_job, args=(job_description,
                job_id, job_name, labeled_data_db_format, playbook_fname,
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
        cur.execute('SELECT state FROM jobs WHERE id=%s', (job_id,))
        return jsonify(cur.fetchone()[0]), 200
    except (IndexError, psycopg2.Error) as e:
        return jsonify('error'), 404


@app.route('/jobs/<job_id>', methods=["GET", "DELETE"])
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


@app.route('/droplets/<droplet_uid>', methods=["DELETE"])
def individual_droplet(droplet_uid):
    # find droplet uid
    cur.execute('''UPDATE droplets SET updated=DEFAULT, status='destroying'
            WHERE uid=%s''',(droplet_uid,)) 
    conn.commit()
    # send delete request to D.O api
    delete_droplets_url = "https://api.digitalocean.com/v2/droplets/{}".format(
            droplet_uid)
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    r = requests.delete(delete_droplets_url, headers=headers)
    if r.status_code == 204:
        # update droplet state in db to deleted
        cur.execute('''UPDATE droplets
                SET updated=DEFAULT, status='destroyed'
                WHERE uid=%s''',(droplet_uid,)) 
        conn.commit()
        return '', 204
    else:
        cur.execute('''UPDATE droplets
                SET updated=DEFAULT, status='failed-to-destroy',
                meta=jsonb_set(meta, '{destroy_failed_response}', %s)
                WHERE uid=%s''',(droplet_uid, r.text)) 
        conn.commit()
        return '', 400


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
    app.run(port=5000, host='0.0.0.0', debug=True)
