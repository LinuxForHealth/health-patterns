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
    -i=*|--inputs=*)
      INPUTS="${i#*=}"
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
echo "INPUTS  = ${INPUTS}"

#docker build services/${NAME} -t ${REPOSITORY}/${NAME}:${TAG}
#docker push ${REPOSITORY}/${NAME}:${TAG}

