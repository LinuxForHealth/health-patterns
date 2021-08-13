# cql-bulkexport

A deployable service that will create a bulk export of patient
data from a list of patient ids returned by a cql library for use
by downstream analytics.  Data is deposited into a COS bucket. This service
relies on the existence of the cohort-service and the FHIR server with
bulk data configured.

## Prerequisites

 - fhir server
   - need to know endpoint, username, password
 - set up fhir server bulk export
   - requires setting up a COS bucket
     - S3 service credentials
     - cos_endpoint
     - cos_api_key
     - cos_instance_crn
     - bucket name

## operations

- listing cql libraries that are available from the cohort service

    (GET)  https://\<cql-bulkexporturl>/cql_libraries

- begin a process to do the following

  - run a cql library returning patient ids
  - bulk export the data for those patients to a COS bucket temporarily
  - create a single COS bucket result for that data removing the temp artifacts

    (GET)  https://\<cql-bulkexporturl>?cql=\<cqlname>

- general health of service-a simple sanity check on the service

    (GET)  https://\<cql-bulkexporturl>/healthcheck
