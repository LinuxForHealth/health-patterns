# health-patterns
health-patterns is a collection of documentation and reference implementations that highlight how to combine various technologies into meaningful patterns for healthcare.


The initial focus will be a clinical data ingestion reference implementation that will accept clinical healthcare data, perform some translation and normalization and then store it into an industry standard FHIR Server.

Subsequent patterns will focus on 
-  Extraction of concepts / named entities using NLP and storing that information back into the FHIR Server
-  De-identification of patient data to be stored into a secondary FHIR Server
-  Patient data Analytics and patient data Access

More information about these patterns including our roadmap can be found [here](roadmap.md)

Components currently used by health-patterns clinical data ingestion reference implementation


- Apache Kafka (https://kafka.apache.org/ is a distributed streaming platform for publishing and subscribing records as well as storing and processing streams of records.  


- NiFi (https://nifi.apache.org/) Apache NiFi is a platform for automating and managing the flow of data between disparate systems. 


- Flink (https://flink.apache.org/) Apache Flink is a framework and distributed processing engine for stateful computations over unbounded and bounded data streams. Flink has been designed to run in all common cluster environments, perform computations at in-memory speed and at any scale.


- HL7-ingestion (https://github.com/Alvearie/HL7-ingestion)


- Health record ingestion (HRI)  (https://github.com/Alvearie/HRI)


- FHIR Server (https://github.com/IBM/FHIR)  The IBM® FHIR® Server is a modular Java implementation of version 4 of the HL7 FHIR specification with a focus on performance and configurability.


- Prometheus (https://prometheus.io/) is an open source monitoring and alerting tool that is widely adopted across many enterprises. Prometheus can be configured to monitor targets by scraping or pulling metrics from the target’s HTTP endpoint and storing the metric name and a set of key-value pairs in a time series database.


- Grafana (https://grafana.com/) is an open source tool for data visualization and monitoring. Data sources such as Prometheus can be added to Grafana for metrics collection. t includes powerful visualization capabilities for graphs, tables, and heatmaps. 


- Jupyter (https://jupyter.org/) The Jupyter Notebook is an open-source web application that allows you to create and share documents that contain live code, equations, visualizations and narrative text. Uses include: data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.



