# cql-bulk-export

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

    (GET)  https://\<cql-bulk-exporturl\>/cql_libraries

- begin a process to do the following

  - run a cql library returning patient ids
  - bulk export the data for those patients to a COS bucket temporarily
  - create a single COS bucket result for that data removing the temp artifacts

    (GET)  https://\<cql-bulk-exporturl\>?cql=\<cqlname>

  - returns a job id that is used to check status

- check status of job (returns working or done)

    (GET)  https://\<cql-bulk-exporturl\>/status?id=\<jobid>

- general health of service-a simple sanity check on the service

    (GET)  https://\<cql-bulk-exporturl\>/healthcheck

## Using the service

This service combines the behavior of the cohorting service and the notion of
bulk export.  The goal is to process data stored in the FHIR server and return an
ndjson formatted file (placed in a COS bucket) that contains all the resources for patients
that satisfy a cohort cql library.  The following outlines the steps required to use the service.

- create a COS bucket and generate credentials
- turn on cohort service
- configure FHIR server bulk export
- configure cql-bulk-export
- store a cql library using cohort service
- use cql-bulk-export service to run that cohort library and create the resulting resource file


### Configuration

Turn on the cohort service by enabling in the `values.yaml` file

```
# ------------------------------------------------------------------------------
# Cohort Service
# ------------------------------------------------------------------------------
cohort-service:
  enabled: true
```

Configure the bulk export functionality on the FHIR server using the generated
service credentials.  For example, these credentials (actual data not shown) get mapped as shown below.

```
{
  "apikey": "aaa",
  "cos_hmac_keys": {
    "access_key_id": "bbb",
    "secret_access_key": "ccc"
  },
  "endpoints": "",
  "iam_apikey_description": "",
  "iam_apikey_name": "",
  "iam_role_crn": "ddd",
  "iam_serviceid_crn": "eee",
  "resource_instance_id": "fff"
}
```

In the `values.yaml` file, fill in the values shown.

```
objectStorage:
  enabled: true
  location: <<your bucket location (for example us-geo)>>
  endpointUrl: <<your bucket endpoint>>
  accessKey: <<access_key_id>>
  secretKey: <<secret_access_key>>
  bulkDataBucketName: <<your bucket>>
```


Configure the cql-bulk-export service by providing information for the three components in the `values.yaml` file.  Again,
use the credentials as well as the FHIR server username/password and proper endpoints.


```
cql-bulk-export:
  enabled: true
  ingress:
    enabled: true
    class: *ingressClass
    hostname: *hostname
  fhir:
    endpoint: <<your fhir endpoint>>
    user: <<your fhir username>>
    password: <<your fhir password>>
  cohort:
    endpoint: <<your cohort-service endpoint>>
  cos:
    endpoint: <<your bucket endpoint>>
    apikey: <<your apikey>>
    instancecrn: <<your iam_serviceid_crn>>
  bucketname: <<your bucket name>>
  resourcelist: "<<blank delimited list of resources to extract>>"
```

### Use Step 1

Use the cohort service to load a cql library.

POST a cql library to ```https://<<your deployment hostname>>/cohort-service/libraries```

For example, the following cql will return patients that are male who are over 40
```
library "MalePatientsOver40" version '1.0.0'

using FHIR version '4.0.1'

include "FHIRHelpers" version '4.0.1' called FHIRHelpers

context Patient

define "Patient is Male":
   Patient.gender.value = 'male'

define "Initial Population":
   "Patient is Male"

define "Denominator":
   "Initial Population"

define "Numerator":
   AgeInYears() > 40
```

This will return the following response
```
CQL created! - URI: https://<<your deployment hostname>>/libraries/MalePatientsOver40-1.0.0
```

### Use Step 2


Start a cql based bulk export for those patients that satisfy a particular cql library.


GET (start a "bulk export")
```
https://<<your deployment hostname>>/cql-bulk-export?cql=MalePatientsOver40-1.0.0
```

You should see a response similar to
```
{
	"message": "Started process to build MalePatientsOver40.ndjson JOB ID=0146f9b2-e5f0-40c3-8c9a-ee2febc01d05",
	"status": "202"
}
```

Note that the response provides the ndjson filename and the job id for the next step.

### Use Step 3

Query the status endpoint using the job id from the previous step.  This should
show the current status of the export (either `working` or `done`)

GET (query the status for done)

```
https://<<your deployment hostname>>/cql-bulk-export/status?id=0146f9b2-e5f0-40c3-8c9a-ee2febc01d05
```

You should see a response similar to the following.

```
{
	"info": {
		"cos_bucket": "<<your bucket name",
		"cos_target": "<<filename>>.ndjson",
		"number_of_patients": 8,
		"number_of_resources": 1717
	},
	"status": "done"
}
```

When status is `done`, query the COS bucket for the file shown.
It will contain the resources from all patients satisfying the cql.
