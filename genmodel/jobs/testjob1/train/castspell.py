import json
import logging
import os
import socket
import subprocess
import psycopg2

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='trainer_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/trainerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('trainer')

try:
    JOB_ID = os.environ['JOB_ID']
    DROPLET_NAME = os.environ['DROPLET_NAME']
    DB_NAME = os.environ.get('DB_NAME', 'nlp')
    DB_PASSWORD = os.environ.get('DB_PASS', '')
    DB_USER = os.environ.get('DB_USER', DB_NAME)
except KeyError as e:
    logger.info('critical environment variables were not set. exiting')
    raise e


def become_wizard():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host='localhost')
    cur = conn.cursor()

    # Check if another droplet has already claimed the defense against the dark
    # arts post. if so exit, if not mark that one is running then continue.
    cur.execute("""UPDATE jobs SET meta=jsonb_set(meta, '{wizard}', %s), updated=DEFAULT
                    WHERE NOT(meta ? 'wizard')
                    AND id=%s
                """, (DROPLET_NAME,JOB_ID))
    conn.commit()
    cur.execute("""SELECT COUNT(*) FROM jobs WHERE
                    meta->'wizard'=%s 
                    AND id=%s
                """,
            (DROPLET_NAME, JOB_ID))
    return cur.fetchone()[0] == 1


def cast_spell():
    inline_pip_args = ""
    with open('spell/requirements.txt') as f:
        for dep in f:
            inline_pip_args += '--pip {} '.format(dep)

    # v100 is the rocket ship, k80 is a volvo
    spell_script = "spell run {pipargs} --env SECRET={secret} --env \
            JOB_ID={job_id} --env API_URL={api_url} --python3 -t k80 python \
            spell/train.py".format(
            secret="TODO", job_id=JOB_ID, api_url="http://206.81.5.140:5000",
            pipargs=inline_pip_args)
    subprocess.call([spell_script])
    logger.info('Avada kedavra!!')

if __name__ == '__main__':
    # attempt to register as wizard
    logger.info('registering as wizard...')
    i_got_my_letter =  become_wizard()
    # cast spell
    if i_got_my_letter:
        logger.info('casting spell...')
        cast_spell()
    else:
        logger.info("you're a muggle harry.")

