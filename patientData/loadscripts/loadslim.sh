#!/bin/bash
# Enter the absolute path and the complete hostname 
echo "enter the hostname for this deployment: "
read hosturl
echo "enter the directory path for the patients: "
read directory
for filename in $directory/*; do
    echo "$filename"
    curl -X POST https://$hosturl/expose-kafka?topic=ingest.topic.in   --retry 3 --header "Content-Type: text/plain" --data-binary  "@$filename"
    sleep 2
done
