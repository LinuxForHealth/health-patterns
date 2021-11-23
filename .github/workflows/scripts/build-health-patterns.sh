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

if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  # Re-Index Helm Charts ##
  helm repo index docs/charts
  printf "\n\n$Helm repo re-indexed"

  # Add all changed files to git
  git add -A

  # Commit/Push updates to Git
  git config user.name "${GITHUB_USER}"
  git commit -m 'Add build artifacts to git commit'
  git push
fi