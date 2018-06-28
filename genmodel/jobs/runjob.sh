#!/usr/bin/env bash

# $./runjob.sh path/to/job
# example: ./runjob.sh testjob1

# create job tarball
tar -zcvf $(basename $1).tar.gz $1

# upload the job tarball to the server with scp
scp $(basename $1).tar.gz root@206.81.5.140:jobs

# supply name of job in post request to start job
curl -d "job=$(basename $1)" -X POST 206.81.5.140:5000/jobs


