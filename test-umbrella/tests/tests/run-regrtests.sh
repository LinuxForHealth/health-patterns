#!/usr/bin/env bash

# Create an regtest.xml test result file that shows "good" or no results for the Insights toolchain

output="<testcase classname=\"bash\" name=\"test1\" time=\"0\"/>"
currentTime=`date +"%Y-%m-%dT%T"`
header="<testsuite name=\"Regression tests\" tests=\"0\" failures=\"0\" errors=\"0\" skipped=\"0\" timestamp=\"${currentTime}\" time=\"0\">"
footer="</testsuite>"

echo "Current Directory"
pwd

cat << EOF > regtest.xml
$header
$output
$footer
EOF