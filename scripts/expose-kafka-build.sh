#!/bin/bash
echo "Hello World"

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
    *)
      # unknown option
      ;;
  esac
done


echo "REPOSITORY  = ${REPOSITORY}"
echo "NAME        = ${NAME}"
echo "TAG         = ${TAG}"

last_ver=is $(docker image ls atclark/expose-kafka --format "{{.Tag}}" | sort -r | head -1)

echo "last_ver  = ${last_ver}"

#docker build services/${NAME} -t ${REPOSITORY}/${NAME}:${TAG}
#docker push ${REPOSITORY}/${NAME}:${TAG}

