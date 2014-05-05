#!/bin/bash
trap 'for i in $(seq 1 7); do echo -n "#"; sleep 1; done; exit' SIGTERM SIGHUP
for i in `seq 1 $1`; do
    echo "3-$i"
    sleep 0.7
done
