# health-patterns
health-patterns is a collection of documentation and cloud agnostic reference implementations of the overall [Alvearie architecture](https://alvearie.io/architecture). They highlight how to combine various technologies into meaningful patterns for healthcare.

To this point, there has been focus on 5 patterns for healthcare data:
1) [**Clinical Data _Ingestion_**](clinical-ingestion)
2) [**Clinical Data _Enrichment_**](clinical-ingestion)  is currently combined with clinical data ingestion but will be separately availalbe in the near future
3) [**Quality Measure & _Cohorting_**](cohort-service)
4) [**Clinical Data _Access_**](data-access)
5) **Clinical Data _Analytics_**  Coming soon


### See a summary of all of the [patterns here](https://alvearie.io/health-patterns/)

Components currently used by health-patterns clinical data ingestion reference implementation


- [Apache Kafka](https://kafka.apache.org/) is a distributed streaming platform for publishing and subscribing records as well as storing and processing streams of records.  


- [NiFi](https://nifi.apache.org/) Apache NiFi is a platform for automating and managing the flow of data between disparate systems. 

- [FHIR Server](https://github.com/IBM/FHIR)  The IBM® FHIR® Server is a modular Java implementation of version 4 of the HL7 FHIR specification with a focus on performance and configurability.

- [HL7-ingestion](https://github.com/Alvearie/HL7-ingestion)

- [Health record ingestion (HRI)](https://github.com/Alvearie/HRI)

- [Quality measure and cohort service](https://github.com/Alvearie/quality-measure-and-cohort-service)

- [De-identification](https://github.com/Alvearie/de-identification)

- [Keycloak](https://www.keycloak.org/)

- [Keycloak extensions for FHIR](https://github.com/Alvearie/keycloak-extensions-for-fhir)

- [FHIR UI / Patient Browser](https://github.com/Alvearie/patient-browser)


- [Flink](https://flink.apache.org/) Apache Flink is a framework and distributed processing engine for stateful computations over unbounded and bounded data streams. Flink has been designed to run in all common cluster environments, perform computations at in-memory speed and at any scale.

- [Prometheus](https://prometheus.io/) is an open source monitoring and alerting tool that is widely adopted across many enterprises. Prometheus can be configured to monitor targets by scraping or pulling metrics from the target’s HTTP endpoint and storing the metric name and a set of key-value pairs in a time series database.


- [Grafana](https://grafana.com/) is an open source tool for data visualization and monitoring. Data sources such as Prometheus can be added to Grafana for metrics collection. t includes powerful visualization capabilities for graphs, tables, and heatmaps. 


- [Jupyter](https://jupyter.org/) The Jupyter Notebook is an open-source web application that allows you to create and share documents that contain live code, equations, visualizations and narrative text. Uses include: data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.
