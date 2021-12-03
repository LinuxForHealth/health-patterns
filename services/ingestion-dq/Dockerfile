FROM busybox:stable
RUN mkdir /dq
WORKDIR /dq
ADD dq-config dq-config
COPY dq-config dq-config
COPY target/scala-2.12/ingestion-dq-assembly*.jar ingestion-dq-assembly.jar
RUN wget -O spark.tgz https://dlcdn.apache.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz;
RUN tar -xzf spark.tgz
RUN mv spark-3.1.2-bin-hadoop3.2 spark
RUN rm -f spark.tgz
