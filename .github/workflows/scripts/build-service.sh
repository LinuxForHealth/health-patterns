#!/bin/bash

##################################################################################
## Build Service General Script
##
## This utility will
##   Build a service from source
##   Generate a docker container
##   Update helm charts referencing the docker container
##   Rebuild the helm package
##   Reindex the helm repository
##   Update the Health Patterns Helm chart to target the new service Helm chart
##   
##   To run, call: 
##     .github/workflows/scripts/build-service.sh
##
##   And include the following parameters:
##
##     -s, --service-name: (Required) The name of the service to build. Expected to be found at services/<<SERVICE_NAME>>
##
##     -o, --organization: (Optional) The name of the organization to use for the docker container.  
##
##     -r, --repository: (Optional) The name of the repository to use for the docker container.  Defaults to <<SERVICE_NAME>>
##
##     -t, --tag: (Optional) The tag value to use for the docker container.  Will generate a new value if omitted.
##
##     -m, --mode: (Optional) The mode to run this tool.  Defaults to "DEV", which will only apply changes necessary to update your local git folder. Defaults to "DEV".
##
##     --github-user: (Optional) Your Github user name. This will be used to generate/push a docker container to your organization.  Either github-user or private-docker-user is required. 
##
##     --docker-user: (Optional) The docker user used for pushes to Alvearie.  Required for mode=push.  Should be "alvearie"
##
##     --docker-token: (Optional) The docker token for docker-user used to authenticate to docker hub.  Required for mode=push. Should be a token capable of pushing to "alvearie" org in docker hub.
##
##     --private-docker-user: (Optional) The user name for your docker hub account.  Allows different usernames between github and docker.  Either github-user or private-docker-user is required.
##################################################################################


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
    -s=*|--service-name=*)
      SERVICE_NAME="${i#*=}"
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


###########################################################
## Find Organization name (i.e. "alvearie" or "atclark") ##
###########################################################
if [ -z "$ORG" ]; then
  printf "\nNo organization provided. Generating based on docker history...\n"
  if [[ ${MODE} == 'DEV' ]]
  then
    if [[ -z "$PRIVATE_DOCKER_USER" ]]
    then
      USER="${GITHUB_USER}"
    else
      USER="${PRIVATE_DOCKER_USER}"
    fi
    ORG=${USER}
  elif [[ ${MODE} == 'push' ]]
  then
    USER=${DOCKER_USER}  
    ORG="alvearie"
  fi
fi


if [ -z "$REPOSITORY" ]; then
  REPOSITORY=${SERVICE_NAME}
fi

#############################
## Generate Tag to be used ##
## last_ver or last_ver++  ##
#############################
if [ -z "$TAG" ]; then
  printf "\nNo tag provided. Generating based on docker history...\n"

  last_tag="$(grep "tag:" services/${SERVICE_NAME}/chart/values.yaml | sed -r 's/\s*tag:\s*(.*)/\1/')"
  last_tag=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 

  last_alvearie_tag="$(wget -q https://registry.hub.docker.com/v1/repositories/alvearie/${SERVICE_NAME}/tags -O -  | sed -e 's/[][]//g' -e 's/"//g' -e 's/ //g' | tr '}' '\n'  | awk -F: '{print $3}'| sort -r --version-sort | sed '/<none>/d' | head -1)"
  last_alvearie_tag=`echo $last_alvearie_tag | sed -e 's/^[[:space:]]*//'` 
  if [ -z "${last_alvearie_tag}" ]; then 
    printf "No previous service tag found. Defaulting to 0.0.1\n"
    last_alvearie_tag='0.0.1'
  fi
 
  printf "last_tag: ${last_tag}\n"
  printf "last_alvearie_tag: ${last_alvearie_tag}\n"
  # Bump value if it matches the last official container tag
  if [[ $last_tag == $last_alvearie_tag ]]
  then
    [[ "$last_tag" =~ (.*[^0-9])([0-9]+)$ ]] && TAG="${BASH_REMATCH[1]}$((${BASH_REMATCH[2]} + 1))"
  else
    # Use the last tag (already bumped compared to official tag)
    TAG=`echo $last_tag | sed -e 's/^[[:space:]]*//'` 
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
if [ ${MODE} == 'push' ]; then
  printf "\nPushing docker image to repostiory: ${ORG}/${REPOSITORY}:{$TAG}\n"

  # Login to Docker
  echo  ${DOCKER_TOKEN} | docker login --username ${USER} --password-stdin
  
  docker push -q ${ORG}/${REPOSITORY}:${TAG}
fi


######################################
## Update helm chart to use new org ##
######################################
last_org="$(grep "repository:" services/${SERVICE_NAME}/chart/values.yaml | sed -r 's/\s*repository:\s*(.*)/\1/' | sed -r 's/(.*)\/'${REPOSITORY}'/\1/')"
last_org=`echo $last_org | sed -e 's/^[[:space:]]*//'` 
printf "last_org: ${last_org}\n"
if [ ${ORG} != ${last_org} ]; then 
  printf "\nUpdating values.yaml with new container image org\n"
  values_file=$(sed -e 's/\(\s*repository:\).*/\1 '${ORG}'\/'${REPOSITORY}'/' services/${SERVICE_NAME}/chart/values.yaml)
  echo "$values_file" > services/${SERVICE_NAME}/chart/values.yaml
  printf "Updated.\n"
fi

##########################################
## Update helm chart to use new version ##
##########################################
if [ ${TAG} != ${last_tag} ]; then 
  printf "\nUpdating values.yaml with new container image version\n"
  values_file=$(sed -e 's/\(\s*tag:\).*/\1 '${TAG}'/' services/${SERVICE_NAME}/chart/values.yaml)
  echo "$values_file" > services/${SERVICE_NAME}/chart/values.yaml
  printf "Updated.\n"
fi


###########################################
## Update helm chart to bump chart.yaml version ##
###########################################
if [ ${MODE} == 'push' ]; then
  last_service_helm_ver="$(grep "version:" services/${SERVICE_NAME}/chart/Chart.yaml | sed -r 's/version: (.*)/\1/')"
  last_service_helm_ver=`echo $last_service_helm_ver | sed -e 's/^[[:space:]]*//'` 
 
  last_alvearie_service_helm_ver="$(wget -q https://raw.githubusercontent.com/Alvearie/health-patterns/main/services/${SERVICE_NAME}/chart/Chart.yaml -O - | grep "version:" | sed -r 's/version: (.*)/\1/')"
  last_alvearie_service_helm_ver=`echo $last_alvearie_service_helm_ver | sed -e 's/^[[:space:]]*//'` 
  if [ -z "${last_alvearie_service_helm_ver}" ]; then 
    printf "No previous service chart version found. Defaulting to 0.0.1\n"
    last_alvearie_service_helm_ver='0.0.1'
  fi

  printf "current chart version: ${last_service_helm_ver}\n"
  printf "current alvearie chart version: ${last_alvearie_service_helm_ver}\n"

  service_helm_ver=${last_service_helm_ver}
  if [ ${last_service_helm_ver} == ${last_alvearie_service_helm_ver} ]; then
    # if PUSH and chart version hasn't been bumped yet from the last pull_request value, bump it here
    [[ "$last_service_helm_ver" =~ ([0-9]+).([0-9]+).([0-9]+)$ ]] && service_helm_ver="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((${BASH_REMATCH[3]} + 1))"
  fi
  printf "new chart version: ${service_helm_ver}\n"
  if [ "${last_service_helm_ver}" != "${service_helm_ver}" ]; then
    printf "\nUpdating chart.yaml with new service helm chart version\n"
    printf "new chart version: ${service_helm_ver}\n"
    chart_file=$(sed -e 's/version: '${last_service_helm_ver}'/version: '${service_helm_ver}'/' services/${SERVICE_NAME}/chart/Chart.yaml)
    echo "$chart_file" > services/${SERVICE_NAME}/chart/Chart.yaml
    printf "Updated.\n"
  fi
fi


if [ ${last_service_helm_ver} != ${service_helm_ver} ] || [ ${TAG} != ${last_tag} ] || [ ${ORG} != ${last_org} ]; then

  ###################################
  ## Re-package service helm chart ##
  ###################################
  helm_package_suffix=$(helm package services/${SERVICE_NAME}/chart -d docs/charts/ | sed "s/.*${SERVICE_NAME}//")
  new_helm_package=${SERVICE_NAME}${helm_package_suffix}
  printf "New Helm Package: ${new_helm_package}\n"

  ########################################################
  ## Copy Helm tgz to health-patterns dependency folder ##
  ########################################################
  if [[ ${MODE} == 'DEV' ]]
  then
    ### Since DEV mode, copy to health-patterns dependency folder
    mkdir -p helm-charts/health-patterns/charts/
	if [ -z "${SERVICE_NAME}" ]; then
      rm helm-charts/health-patterns/charts/${SERVICE_NAME}*.tgz
    fi
    cp docs/charts/${new_helm_package} helm-charts/health-patterns/charts/
  fi

  ##########################
  ## Re-Index Helm Charts ##
  ##########################
  if [ ${MODE} == 'push' ]; then
    helm repo index docs/charts
    printf "\n${SERVICE_NAME}${helm_package_suffix} Helm Chart packaged, repo re-indexed, and packaged chart copied to Health Patterns\n"
  fi

  ##########################
  ## Update Health-Patterns chart.yaml to point at new service chart ##
  ##########################
  if [ ${MODE} == 'push' ]; then
    file="helm-charts/health-patterns/Chart.yaml"
    NEW_CHART=`awk '!f && s{sub(old,new);f=1}/'${SERVICE_NAME}'/{s=1}1; fflush()' old="version: .*" new="version: ${service_helm_ver}" $file`
    if [[ ! -z "$NEW_CHART" ]]
    then
      echo "$NEW_CHART" > $file
      printf "\nUpdated $file to reflect new helm chart version (${service_helm_ver}) for ${SERVICE_NAME}\n"
    fi
  fi
fi 