#!/usr/bin/env bash

# $./runjob.sh path/to/job
# example: ./runjob.sh testjob1
# ./runjob.sh --job=myliljob --hash=

for i in "$@"
do
case $i in
    -j=*|--job=*)
    JOB="${i#*=}"
    shift # past argument=value
    ;;
    -h=*|--hash=*)
    HASH="${i#*=}"
    shift # past argument=value
    ;;
    -r=*|--repo=*)
    REPO="${i#*=}"
    shift # past argument=value
    ;;
    *)
    ;;
esac
done
echo "JOB             = ${JOB}"
echo "HASH            = ${HASH}"
echo "REPO            = ${REPO}"

if [ -z ${JOB} ] || [ -z ${HASH} ] || [ -z ${REPO} ]
then
  echo 'important variables are not set'
  exit 1
else
  curl -d "job=${JOB}&hash=${HASH}&repo=${REPO}" -X POST localhost:5000/jobs
fi

