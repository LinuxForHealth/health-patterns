#!/bin/bash
echo "Hello World"
docker build services/expose-kafka -t atclark/expose-kafka:SNAPSHOT
docker push atclark/expose-kafka:SNAPSHOT

