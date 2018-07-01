#!/usr/bin/env bash

# set droplet ID 
export DROPLET_UID=$(curl -s http://169.254.169.254/metadata/v1/id)
export DROPLET_NAME=$(curl -s http://169.254.169.254/metadata/v1/hostname)

# Start x reducers
cpu_count=$(grep -c ^processor /proc/cpuinfo)
worker_count=$(( cpu_count / 2 ))

# start reducers
reducer_processes=()
for i in {1..$worker_count}
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

# kill all reducers
for p in "${reducer_processes[@]}"; do
  kill -9 $p
done

# start vectorizers
vectorizer_processes=()
for i in {1..$worker_count}
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

# kill all vectorizers
for p in "${vectorizer_processes[@]}"; do
  kill -9 $p
done

# once vectorization is complete, the droplet is no longer needed, droplet makes
# a DELETE request on itself.
curl -X DELETE $JOB_MANAGER/droplets/$DROPLET_UID




