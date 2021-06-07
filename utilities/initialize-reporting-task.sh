#!/bin/sh

NIFI_HOST=$1
NIFI_PORT=$2

# This script creates, configures, and starts a prometheus reporting task for generating
# metrics to be used in grafana dashboards

DATA='{"revision":{"version":"0"},"id":"12345","disconnectedNodeAcknowledged":"false","component":{"type":"org.apache.nifi.reporting.prometheus.PrometheusReportingTask","bundle":{"group":"org.apache.nifi","artifact":"nifi-prometheus-nar","version":"1.12.1"}}}'

echo "> POST http://$NIFI_HOST:$NIFI_PORT/nifi-api/controller/reporting-tasks"
response=$(curl -s -X POST -H "Content-Type: application/json" -d $DATA http://$NIFI_HOST:$NIFI_PORT/nifi-api/controller/reporting-tasks)

uri=$(echo $response | sed -n 's|.*"uri":"\([^"]*\)".*|\1|p')

echo "reporting task uri: $uri"

id=${uri##*/}

echo "reporting task id:$id"

CONFIG='{"component":{"id":"'$id'","name":"PrometheusReportingTask","properties":{"prometheus-reporting-task-metrics-endpoint-port":"12667","prometheus-reporting-task-metrics-send-jvm":"true"}},"revision":{"version":"1"}}'

echo "> PUT $uri"
curl -s -X PUT -H "Content-Type: application/json" -d "$CONFIG" $uri

STATUS='{"revision":{"version":2},"state":"RUNNING"}'
statusUrl=$uri/run-status

echo "> PUT $statusUrl"
curl -s -X PUT -H "Content-Type: application/json" -d "$STATUS" $statusUrl

echo "reporting tasks initialized!"