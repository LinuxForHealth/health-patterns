#!/bin/bash
# Load all patient bundles in the specified directory ($2) to the ingestion deployment at the specified host ($1)
for filename in $2/*; do
    echo "$filename"
    curl -X POST https://$1/expose-kafka?topic=ingest.topic.in   --retry 3  --header "Content-Type: text/plain" --header "AddNLPInsights: true" --data-binary  "@$filename"
    sleep 10
done
