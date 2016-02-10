#!/bin/bash

cd $REPO

docker build -t mc2 .
docker tag -f mc2 qa-mesos-persistence.za.prk-host.net:5000/mc2
docker push qa-mesos-persistence.za.prk-host.net:5000/mc2
