# health-patterns roadmap


## Clinical Data Ingestion

The _Clinical Ingestion_ health pattern with optional _Enrichment_ is a cloud agnostic (has been run on IBM Cloud, AWS, Azure, Google), flexible approach to processing healthcare data and storing it into a FHIR server.
At the most basic level, the Ingestion pattern will read HL7 or FHIR data from a [Kafka](https://kafka.apache.org) topic and use [NiFi](https://github.com/apache/nifi) to orchestrate any desired conversion or validation, and then store the results into the [FHIR Server](https://github.com/ibm/fhir)

- Within the [NiFi](https://github.com/apache/nifi) canvas, the _Clinical Ingestion_ health pattern will:
    - Convert [HL7 to FHIR using technology from LinuxForHealth](https://github.com/LinuxForHealth/hl7v2-fhir-converter)
    - Validate the FHIR data without storing it in the FHIR Server
    - Put the converted/validated data on a Kafka topic for processing by the _Enrichment_ pattern
    - Store the FHIR bundle into the [FHIR Server](https://github.com/ibm/fhir)
    - Handle errors:
        - In case of errors within the bundle, individual resources are retried
        - Errors are reported back to the data integrator via the kafka topic


## Clinical Data Enrichment
The _Clinical Enrichment_ health pattern has been separated from the _Ingestion_ pattern.  It is still available to be deployed and run as part of ingestion, but it can also be set up on its own.
If it is run as part of _Ingestion_ it will Enrich the data as it comes into the environment, before it is stored in the FHIR Server.  It can also be run after the data is persisted in the FHIR server and configured to run on new or changed data.
The goal for this _Enrichment_ pattern is that the enriched data will be written to a FHIR server by default, but because these patterns are just reference implementations, they can be modified and consumed in a number of ways.

_Enrichment_ will read FHIR data from a [Kafka](https://kafka.apache.org) topic and use [NiFi](https://github.com/apache/nifi) to orchestrate the optional types of enrichment such as:
- Convert terminology using the FHIR Terminology Services
- [De-identify](https://github.com/Alvearie/de-identification) the FHIR data
- Run an algorithm such as [ASCVD](https://github.com/Alvearie/health-analytics/tree/main/ascvd)
- Run NLP against the unstructured data such as [FHIR DocumentReference](https://www.hl7.org/fhir/documentreference.html)

The flexibility of this approach allows the consumer to use enrichment at the appropriate time.  For instance, some of the enrichment could happen at Ingestion time (FHIR Terminology for  instance) prior to storing the data, but after the data is persisted in the FHIR Server, Enrichment can run again to only run NLP and/or an analtyic algorithm.



## Clinical Data Access & Cohorting 
The _Clinical Data Access_ pattern provides a reference implementation that uses the [quality measure & cohort service](https://github.com/Alvearie/quality-measure-and-cohort-service) to find patients within the FHIR server that match a given cohort as defined using [CQL](https://cql.hl7.org).

Clinical Data Access pattern will show how to configure access to the FHIR server for traditional access methods
- [SMART on FHIR](https://smarthealthit.org/) using [Keycloak extensions for FHIR](https://github.com/Alvearie/keycloak-extensions-for-fhir)
- Using an API Management solution like [3scale](https://github.com/3scale) 
- Possibly show how to integrate with [OpenEMR](https://www.open-emr.org)


## Clinical Data Analytics
In addition, the _Clinical Data Analytics_ reference implementation will incorporate various types of analytics using Kubeflow.  To begin, we will incorporate all of the analytics found in the _Enrichment_ pattern into Kubeflow by calling the same set of Microservices that were used by Enrichment.

We will have examples of 
- using single patient data from the FHIR server to score against a model
- bulk export data from the FHIR Server, transform the data and run the model/analytic in Kubeflow pipelines against multiple patients
- bulk export data from the FHIR Server and transform it to train a new model
- serving an existing trained model


The main Alvearie page shows the longer term [Alvearie architecture](https://alvearie.io/architecture) 


