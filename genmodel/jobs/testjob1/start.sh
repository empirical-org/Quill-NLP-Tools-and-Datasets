#!/usr/bin/env bash

# ensure envars are loaded
source /root/.bash_profile

# set droplet ID 
export DROPLET_UID=$(curl -s http://169.254.169.254/metadata/v1/id)
export DROPLET_NAME=$(curl -s http://169.254.169.254/metadata/v1/hostname)

# create ssh tunnels for connection to rabbitmq, the database, and the api
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -L 5672:localhost:5672 root@206.81.5.140 &
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -L 5432:localhost:5432 root@206.81.5.140 &
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -L 5000:localhost:5000 root@206.81.5.140 &

# wait for ssh tunnels to be created, ready to go
sleep 10s 

# start pre-reduction publisher
nohup /var/lib/jobs/$JOB_NAME/reducer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/reducer/publisher.py &
prereduction_publisher_process=$!

# start reduction writer
nohup /var/lib/jobs/$JOB_NAME/reducer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/reducer/writer.py &
reduction_writer_process=$!

# Start x reducers
cpu_count=$(grep -c ^processor /proc/cpuinfo)
#worker_count=$(( cpu_count / 2 ))
worker_count=$(( cpu_count / 1 ))

# start reducers
reducer_processes=()
for i in $(seq 1 $worker_count)
do
  nohup /var/lib/jobs/$JOB_NAME/reducer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/reducer/reducer.py &
  reducer_processes+=($!)
done

# wait until reduction is complete
while [ true ]
do
    sleep 1m
    export r=$(curl $JOB_MANAGER/jobs/$JOB_ID/state) && [ $r == \"reduced\" ] && break || continue
done


# TODO: bad code, remove this - fix should be in reducers where job state is
# updated
# wait for all reducers in queue to finish
sleep 1m


# TODO: should we kill reducers and reduction publishers?  maybe just don't
# bother?
# kill all reducers
#for p in "${reducer_processes[@]}"; do
#  kill -9 $p
#done
# kill prereduction publisher and reduction writer
#kill -9 $prereduction_publisher_process
#kill -9 $reduction_writer_process

# start pre-vectorization publisher
nohup /var/lib/jobs/$JOB_NAME/vectorizer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/vectorizer/publisher.py &
prevectorization_publisher_process=$!

# start vectorization writer
nohup /var/lib/jobs/$JOB_NAME/vectorizer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/vectorizer/writer.py &
vectorization_writer_process=$!

# start vectorizers
vectorizer_processes=()
for i in $(seq 1 $worker_count)
do
  nohup /var/lib/jobs/$JOB_NAME/vectorizer/venv/bin/python3 /var/lib/jobs/$JOB_NAME/vectorizer/vectorizer.py &
  vectorizer_processes+=($!)
done

# wait until vectorization is complete
while [ true ]
do
    sleep 2m
    export r=$(curl $JOB_MANAGER/jobs/$JOB_ID/state) && [ $r == \"vectorized\" ] && break || continue
done

# TODO: bad code, remove this - fix should be in reducers where job state is
# updated
# wait for all reducers in queue to finish
sleep 1m

## TODO: do we need to kill these? we delete the droplet anyway. commenting out
## kill all vectorizers
#for p in "${vectorizer_processes[@]}"; do
#  kill -9 $p
#done
## kill prevectorization publisher and vectorization writer
#kill -9 $prevectorization_publisher_process
#kill -9 $vectorization_writer_process

# once vectorization is complete, the droplet is no longer needed, droplet makes
# a DELETE request on itself.
curl -X DELETE $JOB_MANAGER/droplets/$DROPLET_UID




