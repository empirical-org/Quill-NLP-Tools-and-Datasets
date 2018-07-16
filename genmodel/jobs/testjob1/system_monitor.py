import logging
import psutil
import socket
import time
import os

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='sysmonitor_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/systemmonitorlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('reducer')

# periodic sytem info message
psi_msg = "{} {} {}"

while True:
    time.sleep(1)
    cc = psutil.cpu_count()
    cp = psutil.cpu_percent() / cpu_count
    cp = round(cp, 2)
    vm = psutil.virtual_memory().percent
    logger.info(psi_msg.format(cp, cc, vm))
