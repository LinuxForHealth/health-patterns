#!/bin/bash

# Exit script on any error
#set -e


PASSWORD=replace-me

#########################
## Gather input values ##
#########################
for i in "$@"; do
  case $i in
    -p=*|--password=*)
      PASSWORD="${i#*=}"
      shift # past argument=value
      ;;
    *)
      # unknown option
      ;;
  esac
done

# generate FHIR server certificate and keystore, and export FHIR server certificate (PKCS12 format)
keytool -genkey -alias server-key -keystore serverKeystore.p12 -storetype PKCS12 -keyalg RSA -storepass $PASSWORD -validity 730 -keysize 4096 -dname "CN=fhirserver, OU=IBM, O=IBM, L=Rochester, ST=Minnesota, C=US"
keytool -exportcert -alias server-key -keystore serverKeystore.p12 -storetype PKCS12 -storepass $PASSWORD -file server-public-key.crt

# generate Nifi client certificate and keystore, and export Nifi client certificate (PKCS12 format)
keytool -genkey -alias client-key -keystore clientKeystore.p12 -storetype PKCS12 -keyalg RSA -storepass $PASSWORD -validity 730 -keysize 4096 -dname "CN=fhiruser, OU=IBM, O=IBM, L=Rochester, ST=Minnesota, C=US"
keytool -exportcert -alias client-key -keystore clientKeystore.p12 -storetype PKCS12 -storepass $PASSWORD -file client-public-key.crt

# import the FHIR server public key certificate into the Nifi client truststore (PKCS12 format)
keytool -importcert -keystore clientTruststore.p12 -storetype PKCS12 -storepass $PASSWORD -file server-public-key.crt -trustcacerts -noprompt

# import the Nifi client public key certificate into the FHIR server truststore (PKCS12 format)
keytool -importcert -keystore serverTruststore.p12 -storetype PKCS12 -storepass $PASSWORD -file client-public-key.crt -trustcacerts -noprompt


# Connect to kubernetes using service account credentials
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl config set-credentials user --token=$TOKEN

# create secrets for FHIR helm chart (PKCS12 format)
kubectl create secret generic fhir-keystore-secret --from-file=fhirKeyStore=serverKeystore.p12 --from-literal=fhirKeyStorePassword=$PASSWORD
kubectl create secret generic fhir-truststore-secret --from-file=fhirTrustStore=serverTruststore.p12 --from-literal=fhirTrustStorePassword=$PASSWORD