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


######################
## Set default mode ##
######################
if [ -z "$MODE" ]; then
  MODE='DEV'
fi

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

###########################################################
## Find Organization name (i.e. "alvearie" or "atclark") ##
###########################################################
if [ -z "$ORG" ]; then
  printf "\nNo repository provided. Generating based on docker history...\n"
  if [[ ${MODE} == 'DEV' ]]
  then
    ORG=${USER}
  elif [[ ${MODE} == 'PUSH' ]]
  then
    if [[ -z "$PRIVATE_DOCKER_USER" ]]
    then
      ORG="${DOCKER_USER}"
    else
      ORG="${PRIVATE_DOCKER_USER}"
    fi
  else
    ORG="alvearie"
  fi
fi


##################################
## Generate Tag to be used      ##
## last_ver_BUILD or last_ver++ ##
##################################
if [ -z "$TAG" ]; then
  printf "\nNo tag provided. Generating based on docker history...\n"

  last_tag="$(grep "tag:" services/${REPOSITORY}/chart/values.yaml | sed -r 's/\s*tag:\s*(.*)/\1/')"
  last_tag=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 

  last_alvearie_tag="$(wget -q https://registry.hub.docker.com/v1/repositories/alvearie/${REPOSITORY}/tags -O -  | sed -e 's/[][]//g' -e 's/"//g' -e 's/ //g' | tr '}' '\n'  | awk -F: '{print $3}'| sort -r --version-sort | sed '/<none>/d' | head -1)"
 
  printf "last_tag: ${last_tag}\n"
  printf "last_alvearie_tag: ${last_alvearie_tag}\n"

  if [ ${MODE}=='DEV' ] || [ ${MODE}=='PUSH']; then
    # DEV or PUSH Mode
    if [[ $last_tag == $last_alvearie_tag ]]
    then
      printf "last_tag1:$last_tag\n"
      [[ "$last_tag" =~ (.*[^0-9])([0-9]+)$ ]] && TAG="${BASH_REMATCH[1]}$((${BASH_REMATCH[2]} + 1))"
      printf "TAG1:$TAG\n"
    else
      TAG=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 
    fi
  elif [[ ${MODE}=="PR" ]]
  then
    # Pull Request
    TAG=$last_alvearie_tag
  fi
fi

printf "\nORG        = ${ORG}\n"
printf "REPOSITORY  = ${REPOSITORY}\n"
printf "TAG         = ${TAG}\n"


###################
## Build Project ##
###################
# Not Yet Implemented

## 1 ##
########################
## Build Docker image ##
########################
printf "\nBuilding ${ORG}/${REPOSITORY}:${TAG}\n"
docker build -q services/${REPOSITORY} -t ${ORG}/${REPOSITORY}:${TAG}

## 2 ##
#####################################
## Push Docker image to docker hub ##
#####################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  printf "\nPushing docker image to repostiory: ${ORG}/${REPOSITORY}:{$TAG}\n"
  docker push -q ${ORG}/${REPOSITORY}:${TAG}
fi


## 3 ##
##########################################
## Update helm chart to use new version ##
##########################################
printf "\nUpdating values.yaml with new container image version\n"
values_file=$(sed -e 's/\(\s*tag:\).*/\1 '${TAG}'/' services/${REPOSITORY}/chart/values.yaml)
echo "$values_file" > services/${REPOSITORY}/chart/values.yaml
printf "Updated.\n"

## 5 ##
###########################################
## Update helm chart to bump chart.yaml version ##
###########################################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  printf "\nUpdating chart.yaml with new service helm chart version\n"
  currentServiceHelmVer="$(grep "version:" services/${REPOSITORY}/chart/Chart.yaml | sed -r 's/version: (.*)/\1/')"
  if [ ${MODE} == 'PUSH' ]; then
    [[ "$currentServiceHelmVer" =~ ([0-9]+).([0-9]+).([0-9]+)$ ]] && newServiceHelmVer="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((${BASH_REMATCH[3]} + 1))"
  else
    newServiceHelmVer= $currentServiceHelmVer
  fi
  printf "current chart version: ${currentServiceHelmVer}\n"
  printf "new chart version: ${newServiceHelmVer}\n"
  chart_file=$(sed -e 's/version: '${currentServiceHelmVer}'/version: '${newServiceHelmVer}'/' services/${REPOSITORY}/chart/Chart.yaml)
  echo "$chart_file" > services/${REPOSITORY}/chart/Chart.yaml
  printf "Updated.\n"
fi


## 7 ##
###################################
## Re-package service helm chart ##
###################################
helm_package_suffix=$(helm package services/${REPOSITORY}/chart -d docs/charts/ | sed "s/.*${REPOSITORY}//")
new_helm_package=${REPOSITORY}${helm_package_suffix}
printf "New Helm Package: ${new_helm_package}\n"


## 8 ##
########################################################
## Copy Helm tgz to health-patterns dependency folder ##
########################################################
if [[ ${MODE} == 'DEV' ]]
then
  ### Since DEV mode, copy to health-patterns dependency folder
  mkdir -p helm-charts/health-patterns/charts/
  rm helm-charts/health-patterns/${REPOSITORY}*.tgz
  cp docs/charts/${new_helm_package} helm-charts/health-patterns/charts/
fi

## 9 ##
##########################
## Re-Index Helm Charts ##
##########################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  helm repo index docs/charts
  printf "\n${REPOSITORY}${helm_package_suffix} Helm Chart packaged, repo re-indexed, and packaged chart copied to Health Patterns\n"
fi


## 10 ##
##########################
## Update Health-Patterns chart.yaml to point at new service chart ##
##########################
if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PR' ]; then
  file="helm-charts/health-patterns/Chart.yaml"
  NEW_CHART=`awk '!f && s{sub(old,new);f=1}/'${REPOSITORY}'/{s=1}1; fflush()' old="version: .*" new="version: ${newServiceHelmVer}" $file`
  if [[ ! -z "$NEW_CHART" ]]
  then
    echo "$NEW_CHART" > $file
    printf "\nUpdated $file to reflect new helm chart version (${newServiceHelmVer}) for ${REPOSITORY}\n"
  fi
fi