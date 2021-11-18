#!/bin/bash

for i in "$@"; do
  case $i in
    -r=*|--repository=*)
      REPOSITORY="${i#*=}"
      shift # past argument=value
      ;;
    -n=*|--name=*)
      NAME="${i#*=}"
      shift # past argument=value
      ;;
    -t=*|--tag=*)
      TAG="${i#*=}"
      shift # past argument=value
      ;;
    -m=*|--mode=*)
      MODE="${i#*=}"
      shift # past argument=value
      ;;
    -d=*|--debug=*)
      DEBUG=True
      ;;
    *)
      # unknown option
      ;;
  esac
done

if [ -z "$REPOSITORY" ]; then
  echo "No repository provided. Generating based on docker history..."
  if [[ ${MODE} == 'PUSH' ]]
  then
    REPOSITORY=$(docker image ls --format '{{.Repository}}' | grep ${NAME} | sort | uniq -i | sed '/alvearie/d')
    REPOSITORY=${REPOSITORY%/${NAME}}
  else
    REPOSITORY="alvearie"
  fi
fi

l=$(echo ${REPOSITORY} | wc -c)
echo "REPOSITORY  = ${REPOSITORY}"
echo "REPOSITORY Length  =${l}"


if [ -z "$TAG" ]; then
  echo "No tag provided. Generating based on docker history..."
  echo "$(docker image ls ${REPOSITORY}/${NAME} --format '{{.Tag}}')"
  last_tag="$(docker image ls ${REPOSITORY}/${NAME} --format '{{.Tag}}' | sort -r | head -1)"
  echo "last_tag: ${last_tag}"
  if [[ ${MODE} == 'PUSH' ]]
  then
    # COMMIT+PUSH / DEV Mode
    if [[ "$last_tag" == *_BUILD ]]
    then
      echo "Re-using tag from last build: ${last_tag}"
      TAG="${last_tag}"
    else
      TAG="${last_tag}_BUILD"
    fi
  else
    # Commit + Pull Request
    [[ "$last_tag" =~ (.*[^0-9])([0-9]+)$ ]] && TAG="${BASH_REMATCH[1]}$((${BASH_REMATCH[2]} + 1))"
  fi
fi

if [ -z "$MODE" ]; then
  MODE='DEV'
fi

l=$(echo ${REPOSITORY} | wc -c)
echo "REPOSITORY  = ${REPOSITORY}"
echo "REPOSITORY Length  =${l}"
echo "NAME        = ${NAME}"
echo "TAG         = ${TAG}"


###################
## Build Project ##
###################
# Not Yet Implemented

########################
## Build Docker image ##
########################
echo "Building ${REPOSITORY}/${NAME}:{$TAG}"
docker build services/${NAME} -t ${REPOSITORY}/${NAME}:${TAG}

#####################################
## Push Docker image to docker hub ##
#####################################
echo "Pushing ${REPOSITORY}/${NAME}:{$TAG}"
if [[ ${DEBUG}!="True" ]]
then
  docker push ${REPOSITORY}/${NAME}:${TAG}
fi

##########################################
## Update helm chart to use new version ##
##########################################
sed -i '' 's/  tag:.*/  tag: '${TAG}'/' "services/${NAME}/chart/values.yaml"
if [[ ${DEBUG}!="True" ]]
then
  if [ ${MODE} == 'PUSH' ] || [ ${MODE} == 'PUSH' ]; then
    echo ''
    #git add services/${NAME}/chart/values.yaml
  fi
fi

###################################
## Re-package service helm chart ##
###################################
helm_package_suffix=$(helm package services/${NAME}/chart -d docs/charts/ >&1 | sed 's/.*'${NAME}'//')
helm repo index docs/charts
if [[ ${MODE} == 'DEV' ]]
then
  ### Since DEV mode, copy to health-patterns dependency folder
  mkdir -p helm-charts/health-patterns/charts/
  rm helm-charts/health-patterns/${NAME}*.tgz
  cp docs/charts/${NAME}${helm_package_suffix} helm-charts/health-patterns/charts/
fi
echo "${NAME}${helm_package_suffix} Helm Chart packaged, repo re-indexed, and packaged chart copied to Health Patterns"


##############################
## Update parent helm chart ##
##############################
