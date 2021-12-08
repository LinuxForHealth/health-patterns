### 1. Get Linux
FROM alpine:3.7

### 2. Get Java via the package manager
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre \
&& apk add --no-cache wget

### 3. Get Python, PIP
RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

### Get Flask for the app
RUN pip3 install  flask
RUN pip3 install flask-restful
RUN pip3 install requests

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

RUN mkdir /fhir-data-quality
WORKDIR /fhir-data-quality
ADD config config

COPY config config
COPY target/scala-2.12/fhir-data-quality-assembly*.jar fhir-data-quality.jar
COPY fhir_data_quality.py .

RUN wget -O spark.tgz https://dlcdn.apache.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
RUN tar -xzf spark.tgz
RUN mv spark-3.1.2-bin-hadoop3.2 spark
RUN rm -f spark.tgz

ENV FLASK_APP fhir_data_quality.py

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]