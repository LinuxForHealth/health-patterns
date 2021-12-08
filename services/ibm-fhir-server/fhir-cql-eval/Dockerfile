# Build stage
FROM maven:3-openjdk-11-slim AS build
COPY pom.xml /

RUN mvn -B package


# Package stage
FROM ibmcom/ibm-fhir-server

COPY --from=build --chown=1001:0 target/dependency/* /opt/ol/wlp/usr/servers/defaultServer/userlib/
