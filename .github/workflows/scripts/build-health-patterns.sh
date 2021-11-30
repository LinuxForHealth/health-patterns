#!/bin/bash

# Exit script on any error
set -e

#########################
## Gather input values ##
#########################
for i in "$@"; do
  case $i in
    -m=*|--mode=*)
      # DEV / PUSH / PR
      MODE="${i#*=}"
      shift # past argument=value
      ;;
      
    --github-user=*)
      GITHUB_USER="${i#*=}"
      shift # past argument=value
      ;;
    *)
      # unknown option
      ;;
  esac
done


######################
## Set default mode ##
######################
if [ -z "$MODE" ]; then
  MODE='DEV'
fi

printf "\nMode: ${MODE}\n"

if [ ${MODE} == 'push' ] || [ ${MODE} == 'pull_request' ]; then
  # Add all changed files to git
  git add -A

  # Commit/Push updates to Git
  git config user.name "${GITHUB_USER}"
  git commit --signoff -m 'Add build artifacts to git commit' || true #Ignore errors in case no files have changed
  git push || true #Ignore errors in case no files have changed
fi