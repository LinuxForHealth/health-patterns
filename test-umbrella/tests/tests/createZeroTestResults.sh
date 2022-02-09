#!/usr/bin/env bash

# Create a test result file that shows "good" or no results for the Insights toolchain
# Input args:
# 1. results file name
# 2. testsuite name

output="<testcase classname=\"bash\" name=\"skiptests\" time=\"0\"/>"
currentTime=`date +"%Y-%m-%dT%T"`
header="<testsuite name=\"$2 tests\" tests=\"0\" failures=\"0\" errors=\"0\" skipped=\"0\" timestamp=\"${currentTime}\" time=\"0\">"
footer="</testsuite>"

echo "Current Directory"
pwd

cat << EOF > $1
$header
$output
$footer
EOF