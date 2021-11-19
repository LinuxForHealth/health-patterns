#!/bin/bash

# Exit script on any error
set -e

#########################
## Gather input values ##
#########################
for i in "$@"; do
  case $i in
    -o=*|--organization=*)
      ORG="${i#*=}"
      shift # past argument=value
      ;;
    -r=*|--repository=*)
      REPOSITORY="${i#*=}"
      shift # past argument=value
      ;;
    -t=*|--tag=*)
      TAG="${i#*=}"
      shift # past argument=value
      ;;
    -m=*|--mode=*)
      # DEV / PUSH / PR
      MODE="${i#*=}"
      shift # past argument=value
      ;;
    -u=*|--user=*)
      # DEV / PUSH / PR
      GIT_USER="${i#*=}"
      shift # past argument=value
      ;;
    -d=*|--docker_user=*)
      # DEV / PUSH / PR
      DOCKER_USER="${i#*=}"
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
printf "1"
###########################################################
## Find Organization name (i.e. "alvearie" or "atclark") ##
###########################################################
if [ -z "$ORG" ]; then
  printf "2"
  printf "\n\nNo repository provided. Generating based on docker history..."
  printf "3"
  if [[ ${MODE} == 'DEV' ]]
  then
    printf "4"
    ORG=$(docker image ls --format '{{.Repository}}' | grep ${REPOSITORY} | sort | uniq -i | sed '/alvearie/d')
    printf "5"
    ORG=${ORG%/${REPOSITORY}}
    printf "6"
  elif [[ ${MODE} == 'PUSH' ]]
  then
    printf "7"
    if [[ -z "$DOCKER_USER" ]]
    then
      printf "8"
      ORG="${GIT_USER}"
    else
      ORG="${DOCKER_USER}"
      printf "9"
    fi
  else
    ORG="alvearie"
    printf "10"
  fi
fi
printf "11"

#####################################
## Load current images from remote ##
#####################################
# FIXME - should be tagging images with "latest" so we can just pull that ONE to find the other tags (x.y.z) and update that
docker pull ${ORG}/${REPOSITORY} -a -q


##################################
## Generate Tag to be used      ##
## last_ver_BUILD or last_ver++ ##
##################################
if [ -z "$TAG" ]; then
  printf "\n\nNo tag provided. Generating based on docker history..."

  if [[ ${MODE} == 'DEV' ]]
  then
    last_tag="$(docker image ls ${ORG}/${REPOSITORY} --format '{{.Tag}}' | sort -r --version-sort | sed '/<none>/d' | head -1)"
    printf "\nlast_tag: ${last_tag}"
    # DEV Mode
    if [[ "$last_tag" == *_BUILD ]]
    then
      printf "\nRe-using tag from last build: ${last_tag}"
      TAG="${last_tag}"
    else
      TAG="${last_tag}_BUILD"
    fi
  else
    last_tag="$(docker image ls ${ORG}/${REPOSITORY} --format '{{.Tag}}' | sort -r --version-sort | sed '/<none>/d' | sed '/_BUILD/d' | head -1)"
    printf "\nlast_tag: ${last_tag}"
    # Commit + Pull Request
    [[ "$last_tag" =~ (.*[^0-9])([0-9]+)$ ]] && TAG="${BASH_REMATCH[1]}$((${BASH_REMATCH[2]} + 1))"
  fi
fi

printf "\n\nORG        = ${ORG}"
printf "\nREPOSITORY  = ${REPOSITORY}"
printf "\nTAG         = ${TAG}"


###################
## Build Project ##
###################
# Not Yet Implemented

## 1 ##
########################
## Build Docker image ##
########################
printf "\n\nBuilding ${ORG}/${REPOSITORY}:{$TAG}"
docker build -q services/${REPOSITORY} -t ${ORG}/${REPOSITORY}:${TAG}

## 2 ##
#####################################
## Push Docker image to docker hub ##
#####################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  printf "\n\nPushing docker image to repostiory: ${ORG}/${REPOSITORY}:{$TAG}"
  docker push -q ${ORG}/${REPOSITORY}:${TAG}
fi


## 3 ##
##########################################
## Update helm chart to use new version ##
##########################################
printf "\n\nUpdating values.yaml with new container image version"
sed -i '' 's/  tag:.*/  tag: '${TAG}'/' "services/${REPOSITORY}/chart/values.yaml"

## 4 ##
###########################################
## Add updated values.yaml to git commit ##
###########################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  file="services/${REPOSITORY}/chart/values.yaml"
  git add ${file}
  printf "\n\nAdded ${file} to Git commit"
fi

## 5 ##
###########################################
## Update helm chart to bump chart.yaml version ##
###########################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  currentServiceHelmVer="$(grep "version:" services/expose-kafka/chart/Chart.yaml | sed -r 's/version: (.*)/\1/')"
  [[ "$currentServiceHelmVer" =~ ([0-9]+).([0-9]+).([0-9]+)$ ]] && newServiceHelmVer="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((${BASH_REMATCH[3]} + 1))"
  printf "\n\nUpdating ${REPOSITORY} helm chart to new version: ${newServiceHelmVer}"
  sed -i '' "s/version: ${currentServiceHelmVer}/version: ${newServiceHelmVer}/" "services/${REPOSITORY}/chart/Chart.yaml"
fi

## 6 ##
###########################################
## Add updated chart.yaml to git commit ##
###########################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  file="services/${REPOSITORY}/chart/Chart.yaml"
  git add ${file}
  printf "\n\nAdded ${file} to Git commit"
fi

## 7 ##
###################################
## Re-package service helm chart ##
###################################
helm_package_suffix=$(helm package services/${REPOSITORY}/chart -d docs/charts/ >&1 | sed 's/.*'${REPOSITORY}'//')

## 7.5 ##
###################################
## Add tgz to Git ##
###################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  file="docs/charts/${REPOSITORY}${helm_package_suffix}"
  git add ${file}
  printf "\n\nAdded ${file} to Git commit"
fi

## 8 ##
########################################################
## Copy Helm tgz to health-patterns dependency folder ##
########################################################
if [[ ${MODE} == 'DEV' ]]
then
  ### Since DEV mode, copy to health-patterns dependency folder
  mkdir -p helm-charts/health-patterns/charts/
  rm helm-charts/health-patterns/${REPOSITORY}*.tgz
  cp docs/charts/${REPOSITORY}${helm_package_suffix} helm-charts/health-patterns/charts/
fi

## 9 ##
##########################
## Re-Index Helm Charts ##
##########################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  helm repo index docs/charts
  printf "\n\n${REPOSITORY}${helm_package_suffix} Helm Chart packaged, repo re-indexed, and packaged chart copied to Health Patterns"
fi

## 9.5 ##
###################################
## Add index.yaml to Git ##
###################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  file="docs/charts/index.yaml"
  git add ${file}
  printf "\n\nAdded ${file} to Git commit"
fi

## 10 ##
##########################
## Update Health-Patterns chart.yaml to point at new service chart ##
##########################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
file="helm-charts/health-patterns/Chart.yaml"
  awk "/${REPOSITORY}/ && a!=1 {print;getline; sub(/version: ${currentServiceHelmVer}/,\"version: ${newServiceHelmVer}\");a=1}1"  ${file} > ${file}
  printf "\n\nUpdated ${file} to reflect new helm chart version (${newServiceHelmVer}) for ${REPOSITORY}"
fi

##############################
## Update parent helm chart ##
##############################

printf "\n\n"
