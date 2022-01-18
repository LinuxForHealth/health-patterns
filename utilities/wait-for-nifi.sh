#!/bin/bash
# This script waits for a NiFi server running on this host to fully initialize.

NIFI_HOST=$1
NIFI_PORT=$2
BEARER_TOKEN=$3

echo "wait for flow controller initialization..."
initializing='initializing'
echo "> https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status"
response=$(curl -s -k -X GET --url https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status -H 'Authorization: Bearer '$BEARER_TOKEN)
echo "< $response"

while [[ "$response" == *"$initializing"* ]];
do
  echo "> https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status"
  response=$(curl -s -k -X GET --url https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/status -H 'Authorization: Bearer '$BEARER_TOKEN)
  echo "< $response"
  sleep 5
done
echo "wait for flow controller initialization...done!"

echo "wait for cluster connection..."
cluster='connectedToCluster":true'
while [[ "$response" != *"$cluster"* ]];
do
  echo "> https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary"
  response=$(curl -s -k -X GET --url https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary -H 'Authorization: Bearer '$BEARER_TOKEN)
  echo "< $response"
  sleep 2
done
echo "wait for cluster connection...done!"

echo "wait for node to show connected..."
connected='connectedNodeCount":1'
while [[ "$response" != *"$connected"* ]];
do
  echo "> https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary"
  response=$(curl -s -k -X GET --url https://$NIFI_HOST:$NIFI_PORT/nifi-api/flow/cluster/summary -H 'Authorization: Bearer '$BEARER_TOKEN)
  echo "< $response"
  sleep 2
done
echo "wait for node to show connected...done!"

echo "nifi cluster is connected and ready to respond to api!"
