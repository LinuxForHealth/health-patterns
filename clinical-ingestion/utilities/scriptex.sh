#!/bin/sh

# This script creates, configures, and starts a prometheus reporting task for generating
# metrics to be used in grafana dashboards

DATA='{"revision":{"version":"0"},"id":"12345","disconnectedNodeAcknowledged":"false","component":{"type":"org.apache.nifi.reporting.prometheus.PrometheusReportingTask","bundle":{"group":"org.apache.nifi","artifact":"nifi-prometheus-nar","version":"1.12.1"}}}'

response=$(curl -X POST -H "Content-Type: application/json" -d $DATA http://ingestion-nifi-0:8080/nifi-api/controller/reporting-tasks)
echo $response
uri=$(echo $response | sed -n 's|.*"uri":"\([^"]*\)".*|\1|p')

echo $uri

id=${uri##*/}

echo $id

CONFIG='{"component":{"id":"'$id'","name":"PrometheusReportingTask","properties":{"prometheus-reporting-task-metrics-endpoint-port":"12667","prometheus-reporting-task-metrics-send-jvm":"true"}},"revision":{"version":"1"}}'

echo $CONFIG

curl -X PUT -H "Content-Type: application/json" -d "$CONFIG" $uri


STATUS='{"revision":{"version":2},"state":"RUNNING"}'
statusUrl=$uri/run-status

echo $statusUrl

curl -X PUT -H "Content-Type: application/json" -d "$STATUS" $statusUrl
