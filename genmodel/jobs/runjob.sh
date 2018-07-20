#!/usr/bin/env bash

# $./runjob.sh path/to/job
# example: ./runjob.sh testjob1

# create job tarball
tar -zcvf $(basename $1).tar.gz $1

# upload the job tarball to the server with scp
scp $(basename $1).tar.gz root@206.81.5.140:jobs


HERE=$PWD
HASH=$(cd $1 && git log -n 1 --pretty=format:"%H")
cd $HERE

# supply name of job in post request to start job
#curl -d "job=$(basename $1)" -X POST 206.81.5.140:5000/jobs
curl -d "job=$(basename $1)" -X POST localhost:5000/jobs


