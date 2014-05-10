#!/bin/bash
if test "$#" -ne 3
then
    echo 'usage: bash outputd.sh <identifier number> <loop count> <sleep>'
    exit 1
fi
trap 'for i in $(seq 1 7); do echo -n "#"; sleep 1; done; exit' SIGTERM SIGHUP
for i in `seq 1 $2`; do
    echo "$1-$i"
    sleep $3
done
