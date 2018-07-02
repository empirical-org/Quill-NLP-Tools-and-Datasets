from flask import Flask, request, render_template, jsonify
from tabulate import tabulate
from uuid import uuid4
import csv
import logging
import os
import psycopg2
import requests
import subprocess
import tarfile
import threading
import time
import yaml

# set up logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    filename='/root/jobs/jobmanager.log',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger('job-manager-api')



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

    # update droplet status, and set other attrs
    cur.execute("""UPDATE droplets 
                SET status='active',
                    memory=%s,	
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
                """, (droplet_uid, drop['memory'], drop['vcpus'], drop['disk'],
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
    cur.execute("INSERT INTO jobs (name,state) values (%s, %s)",
            (job_name, 'initialized'))
    conn.commit()
    cur.execute('SELECT id FROM jobs WHERE name = %s', (job_name,))
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
            logger.debug("adding labled data to database...")
            # insert data
            reader = csv.reader(labeled_data_stream)
            for row in reader:
                logger.debug('read row, {}'.format(row))
                cur.execute("INSERT INTO labeled_data (data, label, job_id) values(%s, %s, %s)",
                        (row[0], row[1], job_id))
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


def run_job(job_description, job_id, job_name, labeled_data_fname, playbook_fname):
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
        print('middle job 2')
        
        # wait 10s to make sure all droplets are really online + responsive
        time.sleep(10)

        # run ansible on the droplets to install dependencies, job bundle,
        # set environment variables, create ssh tunnels, start jobs 
        logger.info("installing dependencies and starting jobs on remote droplet(s)")
        hosts_string = ':'.join(droplet_ids)
        ansible_command = 'ansible-playbook {} -i \
                /etc/ansible/digital_ocean.py --list-hosts -e \
                hosts_string={} -e job_id={} -e job_name={}'.format(
                        playbook_fname, hosts_string, job_id, job_name)
        output = subprocess.check_output(['bash','-c', ansible_command])
        logger.info("droplets working, job {}-{} started successfully".format(
            job_name, job_id))
    except psycopg2.Error as e:
        ref = '\nhttps://www.postgresql.org/docs/current/static/errcodes-appendix.html'
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
            with tarfile.open('/root/jobs/{}.tar.gz'.format(job_name)) as tar:
                # save ref to labeled data stream
                ld_fname = '{}/labeled_data.csv'.format(job_name)
                labeled_data_stream = tar.extractfile(ld_fname)
                labeled_data_fname = 'labeled_data_{}.csv'.format(str(uuid4())[:8])
                with open(labeled_data_fname, 'wb') as ld:
                    ld.write(labeled_data_stream.read())
                labeled_data_stream.close()

                # make job description dictionary
                jd_fname = '{}/description.yml'.format(job_name)
                job_description_stream = tar.extractfile(jd_fname)
                job_description = yaml.load(job_description_stream)
                job_description_stream.close()
                job_description = set_droplet_names(job_description)

                # save playbook to temporary local file
                zipped_playbook_fname = '{}/playbook.yml'.format(job_name)
                playbook_stream = tar.extractfile(zipped_playbook_fname)
                playbook_fname = 'playbook_{}.yml'.format(str(uuid4())[:8])
                with open(playbook_fname, 'wb') as pb:
                    pb.write(playbook_stream.read())
                playbook_stream.close()

            # initialize job in database (job.state, initialized)
            job_id = initizialize_job_in_database(job_name)
            thr = threading.Thread(target=run_job, args=(job_description,
                job_id, job_name, labeled_data_fname, playbook_fname), kwargs={})
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


@app.route('/jobs/<job_id>/state', methods=["GET"])
def get_job_status(job_id):
    try:
        cur.execute('SELECT state FROM jobs WHERE job_id=%s', (job_id,))
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
    cur.execute('''UPDATE droplet SET updated=DEFAULT, status="destroying"
            WHERE uid=%s''',(droplet_uid)) 
    conn.commit()
    # send delete request to D.O api
    delete_droplets_url = "https://api.digitalocean.com/v2/droplets/{}".format(
            droplet_uid)
    headers = {}
    headers['Authorization'] = 'Bearer {}'.format(os.environ.get('DO_API_TOKEN', ''))
    r = requests.delete(delete_droplets_url, headers=headers)
    if r.status_code == 204:
        # update droplet state in db to deleted
        cur.execute('''UPDATE droplet
                SET updated=DEFAULT, status="destroyed"
                WHERE uid=%s''',(droplet_uid)) 
        conn.commit()
        return '', 204
    else:
        cur.execute('''UPDATE droplet
                SET updated=DEFAULT, status="failed-to-destroy",
                meta=jsonb_set(meta, '{destroy_failed_response}', %s)
                WHERE uid=%s''',(droplet_uid, r.text)) 
        conn.commit()
        return '', 400


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1', debug=True)
