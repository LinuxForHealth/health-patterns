#!/bin/bash
# This script waits for a NiFi server running on this host to fully initialize.

NIFI_HOST=$1
NIFI_PORT=$2

echo "waiting for NiFi API to start nifi $NIFI_PORT"
until nc -vzw 1 $NIFI_HOST $NIFI_PORT; do
  echo "waiting for nifi api..."
  sleep 5
done

echo "wait for flow controller initialization..."
initializing='initializing'
echo "> http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status"
response=$(curl -s -k -X GET --url http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status)
echo "< $response"

while [[ "$response" == *"$initializing"* ]];
do
  echo "> http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status"
  response=$(curl -s -k -X GET --url http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status)
  echo "< $response"
  sleep 5
done
echo "wait for flow controller initialization...done!"

echo "wait for cluster connection..."
cluster='connectedToCluster":true'
while [[ "$response" != *"$cluster"* ]];
do
  echo "> http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary"
  response=$(curl -s -k -X GET --url http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary)
  echo "< $response"
  sleep 2
done
echo "wait for cluster connection...done!"

echo "wait for node to show connected..."
connected='connectedNodeCount":1'
while [[ "$response" != *"$connected"* ]];
do
  echo "> http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary"
  response=$(curl -s -k -X GET --url http://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary)
  echo "< $response"
  sleep 2
done
echo "wait for node to show connected...done!"

echo "nifi cluster is connected and ready to respond to api!"
