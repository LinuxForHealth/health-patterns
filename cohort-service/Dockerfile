# In the short term, we are using the OpenJDK for UBI. Long term, we will use
# the IBM Java Small Footprint JVM (SFJ) for UBI, but that is not in public
# Docker at the moment.
# (https://github.com/ibmruntimes/ci.docker/tree/master/ibmjava/8/sfj/ubi-min)
FROM adoptopenjdk/openjdk8

LABEL maintainer="Luis A. Garcia at Alvearie"

RUN mkdir /opt/app
COPY target/cohort-service-1.0-SNAPSHOT.jar /opt/app/app.jar

ENTRYPOINT [ "sh", "-c", "java -jar /opt/app/app.jar" ]
