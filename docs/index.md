# Welcome to health-patterns

health-patterns is where to find cloud agnostic reference implementations for the overall Alvearie architecture (https://alvearie.github.io/architecture) that incorporate best practices using open technologies.  
The conceptual architecture below is brought into reality with a combination of implementations and documentation.  

![AlvearieConceptualArchitecture](images/AlvearieConceptualArchitecture.png)

Below are the initial patterns that incorporate parts of [Alvearie](https://alvearie.github.io/) along with other open technologies that can be used to start building your own healthcare solutions using a common base of proven technology.

### Clinical Data Ingestion & Enrichment
This pattern provides a reference implementation that can take clinical data in a variety of formats, convert and normalize the data as necessary, optionally enrich it (eg using NLP or de-identification) and store it in a FHIR Server (https://github.com/ibm/fhir)

The Enrichment process can either be run as part of the ingestion or it can run on its own (after the data has been stored in the FHIR Server).

Get started using the clinical data ingestion & enrichment pattern now: https://github.com/Alvearie/health-patterns/tree/main/clinical-ingestion

Learn more about the current state and future enhancements in the [roadmap](roadmap.md)


### Clinical Data Access & Analytics (not yet started)
Clinical Data Access & Analytics
This pattern shows the best practices for accessing the data once it is in the FHIR Server.  This can take the form of direct access using FHIR APIs (direct APIs or bulk data export).   It can also use the cohort & measure service to select a specific clinical cohort.  The data analytics pattern will provide examples of ML & AI choreography using Kubeflow and explain how to easily add additional analytics to derive insights about an individual patient or a cohort of patients.

Learn more about our plans for this pattern in our [roadmap](roadmap.md)

