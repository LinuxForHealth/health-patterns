# Build stage
FROM maven:3-jdk-8-slim AS build

RUN mvn dependency:copy -Dartifact=com.ibm.fhir:fhir-smart:LATEST -DoutputDirectory=target/dependency && \
  mvn dependency:copy -Dartifact=com.ibm.fhir:fhir-ig-us-core:LATEST -DoutputDirectory=target/dependency


# Package stage
FROM ibmcom/ibm-fhir-server

COPY --from=build --chown=1001:0 target/dependency/* /opt/ol/wlp/usr/servers/defaultServer/userlib/
