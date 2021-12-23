FROM bitnami/kubectl:1.20.9 as kubectl

### 1. Get Linux
FROM alpine:3.9

### 2. Get Java via the package manager
RUN apk update \
&& apk upgrade \
&& apk add --no-cache openjdk8-jre bash nss openssl

COPY --from=kubectl /opt/bitnami/kubectl/bin/kubectl /usr/local/bin/
RUN chmod +x /usr/local/bin/kubectl

COPY gen_certs.sh /
RUN chmod +x /gen_certs.sh

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

CMD /gen_certs.sh --password=$PASSWORD