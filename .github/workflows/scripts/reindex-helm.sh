#!/bin/bash

# Exit script on any error
set -e

#########################
## Gather input values ##
#########################
for i in "$@"; do
  case $i in
    --github-user=*)
      GITHUB_USER="${i#*=}"
      shift # past argument=value
      ;;
    --docker-user=*)
      DOCKER_USER="${i#*=}"
      shift # past argument=value
      ;;
    --docker-token=*)
      DOCKER_TOKEN="${i#*=}"
      shift # past argument=value
      ;;
    --private-docker-user=*)
      PRIVATE_DOCKER_USER="${i#*=}"
      shift # past argument=value
      ;;
    --private-docker-token=*)
      PRIVATE_DOCKER_TOKEN="${i#*=}"
      shift # past argument=value
      ;;
    *)
      # unknown option
      ;;
  esac
done


printf "\nMode: ${MODE}\n"

if [ -z "$PRIVATE_DOCKER_USER" ]; then
  USER=${DOCKER_USER}
  TOKEN=${DOCKER_TOKEN}
else
  USER=${PRIVATE_DOCKER_USER}
  TOKEN=${PRIVATE_DOCKER_TOKEN}
fi

#####################
## Login to Docker ##
#####################
echo  ${TOKEN} | docker login --username ${USER} --password-stdin


if [ -z "$PRIVATE_DOCKER_USER" ]; then
  USER=${DOCKER_USER}
  TOKEN=${DOCKER_TOKEN}
else
  USER=${PRIVATE_DOCKER_USER}
  TOKEN=${PRIVATE_DOCKER_TOKEN}
fi


##########################################
## Re-Index Helm Charts and push to Git ##
##########################################
helm repo index docs/charts

###################################
## Add index.yaml to Git ##
###################################
file="docs/charts/index.yaml"
git add ${file}
printf "\n\nAdded ${file} to Git commit"

################################
## Commit/Push updates to Git ##
################################
git config user.name "${GITHUB_USER}"
git commit -m 'Add build artifacts to git commit'
git pull
git merge -s recursive -X ours
git push


printf "\n\n"
