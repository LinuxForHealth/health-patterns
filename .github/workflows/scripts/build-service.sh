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
      # DEV / push / pull_request
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
  elif [[ ${MODE} == 'push' ]]
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


#############################
## Generate Tag to be used ##
## last_ver or last_ver++  ##
#############################
if [ -z "$TAG" ]; then
  printf "\nNo tag provided. Generating based on docker history...\n"

  last_tag="$(grep "tag:" services/${REPOSITORY}/chart/values.yaml | sed -r 's/\s*tag:\s*(.*)/\1/')"
  last_tag=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 

  last_alvearie_tag="$(wget -q https://registry.hub.docker.com/v1/repositories/alvearie/${REPOSITORY}/tags -O -  | sed -e 's/[][]//g' -e 's/"//g' -e 's/ //g' | tr '}' '\n'  | awk -F: '{print $3}'| sort -r --version-sort | sed '/<none>/d' | head -1)"
  last_alvearie_tag=`echo $last_alvearie_tag | sed -e 's/^[[:space:]]*//'` 
  if [ -z "${last_alvearie_tag}" ]; then 
    printf "No previous service tag found. Defaulting to 0.0.1\n"
    last_alvearie_tag='0.0.1'
  fi
 
  printf "last_tag: ${last_tag}\n"
  printf "last_alvearie_tag: ${last_alvearie_tag}\n"

  if [ ${MODE}=='DEV' ] || [ ${MODE}=='push']; then
    # DEV or PUSH Mode
    # Bump value if it matches the last official container tag
    if [[ $last_tag == $last_alvearie_tag ]]
    then
      [[ "$last_tag" =~ (.*[^0-9])([0-9]+)$ ]] && TAG="${BASH_REMATCH[1]}$((${BASH_REMATCH[2]} + 1))"
    else
      # Use the last tag (already bumped compared to official tag)
      TAG=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 
    fi
  elif [[ ${MODE}=="pull_request" ]]
  then
    # Pull Request
    # Always use the last tag (will be bumped from the PUSH action)
    TAG=$last_tag
  fi
fi

printf "\nORG        = ${ORG}\n"
printf "REPOSITORY  = ${REPOSITORY}\n"
printf "TAG         = ${TAG}\n"


###################
## Build Project ##
###################
# Not Yet Implemented


########################
## Build Docker image ##
########################
printf "\nBuilding ${ORG}/${REPOSITORY}:${TAG}\n"
docker build -q services/${REPOSITORY} -t ${ORG}/${REPOSITORY}:${TAG}


#####################################
## Push Docker image to docker hub ##
#####################################
if [ ${MODE} == 'push' ] || [ ${MODE} == 'pull_request' ]; then
  printf "\nPushing docker image to repostiory: ${ORG}/${REPOSITORY}:{$TAG}\n"
  docker push -q ${ORG}/${REPOSITORY}:${TAG}
fi


##########################################
## Update helm chart to use new version ##
##########################################
if [ ${TAG} != ${last_tag} ]; then 
  printf "\nUpdating values.yaml with new container image version\n"
  values_file=$(sed -e 's/\(\s*tag:\).*/\1 '${TAG}'/' services/${REPOSITORY}/chart/values.yaml)
  echo "$values_file" > services/${REPOSITORY}/chart/values.yaml
  printf "Updated.\n"
fi


###########################################
## Update helm chart to bump chart.yaml version ##
###########################################
if [ ${MODE} == 'push' ] || [ ${MODE} == 'pull_request' ]; then
  last_service_helm_ver="$(grep "version:" services/${REPOSITORY}/chart/Chart.yaml | sed -r 's/version: (.*)/\1/')"
  last_service_helm_ver=`echo $last_service_helm_ver | sed -e 's/^[[:space:]]*//'` 
 
  last_alvearie_service_helm_ver="$(wget -q https://raw.githubusercontent.com/Alvearie/health-patterns/main/services/${REPOSITORY}/chart/Chart.yaml -O - | grep "version:" | sed -r 's/version: (.*)/\1/')"
  last_alvearie_service_helm_ver=`echo $last_alvearie_service_helm_ver | sed -e 's/^[[:space:]]*//'` 
  if [ -z "${last_alvearie_service_helm_ver}" ]; then 
    printf "No previous service chart version found. Defaulting to 0.0.1\n"
    last_alvearie_service_helm_ver='0.0.1'
  fi

  printf "current chart version: ${last_service_helm_ver}\n"
  printf "current alvearie chart version: ${last_alvearie_service_helm_ver}\n"

  service_helm_ver=${last_service_helm_ver}
  if [ ${MODE} == 'push' ]; then
    if [ ${last_service_helm_ver} == ${last_alvearie_service_helm_ver} ]; then
      # if PUSH and chart version hasn't been bumped yet from the last pull_request value, bump it here
      [[ "$last_service_helm_ver" =~ ([0-9]+).([0-9]+).([0-9]+)$ ]] && service_helm_ver="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((${BASH_REMATCH[3]} + 1))"
    fi
  fi
  printf "new chart version: ${service_helm_ver}\n"
  if [ "${last_service_helm_ver}" != "${service_helm_ver}" ]; then
    printf "\nUpdating chart.yaml with new service helm chart version\n"
    printf "new chart version: ${service_helm_ver}\n"
    chart_file=$(sed -e 's/version: '${last_service_helm_ver}'/version: '${service_helm_ver}'/' services/${REPOSITORY}/chart/Chart.yaml)
    echo "$chart_file" > services/${REPOSITORY}/chart/Chart.yaml
    printf "Updated.\n"
  fi
fi


if [ ${last_service_helm_ver} != ${service_helm_ver} ] || [ ${TAG} != ${last_tag} ]; then

  ###################################
  ## Re-package service helm chart ##
  ###################################
  helm_package_suffix=$(helm package services/${REPOSITORY}/chart -d docs/charts/ | sed "s/.*${REPOSITORY}//")
  new_helm_package=${REPOSITORY}${helm_package_suffix}
  printf "New Helm Package: ${new_helm_package}\n"

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

  ##########################
  ## Re-Index Helm Charts ##
  ##########################
  if [ ${MODE} == 'push' ] || [ ${MODE} == 'pull_request' ]; then
    helm repo index docs/charts
    printf "\n${REPOSITORY}${helm_package_suffix} Helm Chart packaged, repo re-indexed, and packaged chart copied to Health Patterns\n"
  fi

  ##########################
  ## Update Health-Patterns chart.yaml to point at new service chart ##
  ##########################
  if [ ${MODE} == 'push' ] || [ ${MODE} == 'pull_request' ]; then
    file="helm-charts/health-patterns/Chart.yaml"
    NEW_CHART=`awk '!f && s{sub(old,new);f=1}/'${REPOSITORY}'/{s=1}1; fflush()' old="version: .*" new="version: ${service_helm_ver}" $file`
    if [[ ! -z "$NEW_CHART" ]]
    then
      echo "$NEW_CHART" > $file
      printf "\nUpdated $file to reflect new helm chart version (${service_helm_ver}) for ${REPOSITORY}\n"
    fi
  fi
fi 