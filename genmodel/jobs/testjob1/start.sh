#!/usr/bin/env bash

job_name=$1
job_id=$2

# Start x reducers
cpu_count=$(grep -c ^processor /proc/cpuinfo)
reducer_count=$(( cpu_count / 2 ))

# start reducers
for i in {1..$reducer_count}
do
  /var/lib/jobs/$job_name/reducer/venv/bin/python3 /var/lib/jobs/$job_name/reducer/reducer.py
done

# wait until reduction is complete
while [ true ]
do
    echo "loop body here..."
    curl $JOB_MANAGER/jobs/$job_id/status
    # TODO: if status of job shows reduction is complete, break
    sleep 1m
done

# start vectorizers
for i in {1..$reducer_count}
do
  /var/lib/jobs/$1/vectorizer/venv/bin/python3 /var/lib/jobs/$1/vectorizer/vectorizer.py
done
