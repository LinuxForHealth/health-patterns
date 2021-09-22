# Snomed to ICD10

This project contains a REST API to calculate ICD10 codes from Snomed codes.  There are currently two implementations: one that relies on FHIR Term Graph support to store the mapping information, and one that directly consumes the map data from a source file.

## Technical details

This project uses Quarkus, the Supersonic Subatomic Java Framework. If you want to learn more about Quarkus, please visit its website: https://quarkus.io/ .

## Building the project.

You can build this project using: ``mvn package``

## Running the model from a docker container:

You can deploy this API to kubernetes using the supplied kubernetes.yaml.  First, it will need to be updated to include correct environment variables pointing to your FHIR TermGraph JanusGraph.

For the FHIR TermGraph-based API, Update the following environment variables:
- STORAGE_HOSTNAME ------ This should match your Cassandra service name
- STORAGE_PORT ---------- (Optional) This is the port number used to access Cassandra
- STORAGE_USERNAME ------ This is the user name used to access Cassandra
- STORAGE_PASSWORD ------ This is the password for STORAGE_USERNAME used to access Cassandra. Be sure to supply safely for secure deployments 
- INDEX_SEARCH_HOSTNAME - This should match your ElasticSearch service name
- INDEX_SEARCH_PORT ----- (Optional) This is the port number used to access ElasticSearch

For the direct-from-map-file API, update the following environment variables:
- COS_ENDPOINT -------- The endpoint for your COS bucket
- COS_BUCKET_LOCATION - The geography for your COS bucket (i.e. "us")
- COS_SERVICE_CRN ----- The credentials used to access your COS bucket (See "resource_instance_id" under Service Credentials in IBM Cloud)
- COS_API_KEY_ID ------ The API Key used to access your COS bucket (See "apikey" under Service Credentials in IBM Cloud)
- COS_AUTH_ENDPOINT --- The authority endpoint. (i.e. "https://iam.cloud.ibm.com/identity/token")
- COS_BUCKET_NAME ----- The name of your COS bucket where the map file is stored.

Note: The map file MUST be named "der2_iisssccRefset_ExtendedMapFull_US1000124_20210901.txt" and can be downloaded from: [https://download.nlm.nih.gov/mlb/utsauth/USExt/SnomedCT_USEditionRF2_PRODUCTION_20210901T120000Z.zip](https://download.nlm.nih.gov/mlb/utsauth/USExt/SnomedCT_USEditionRF2_PRODUCTION_20210901T120000Z.zip)


Once you've updated the environment variables properly, deploy using:

```
kubectl apply -f kubernetes.yaml
```

Once the image is deployed, you can access the Term-Graph based API using:

```
curl "http://<<HOST_NAME>>:8080?code=<<SNOMED_CODE>>
```


And you can access the map file-based API using:

```
curl "http://<<HOST_NAME>>:8080/direct?code=<<SNOMED_CODE>>
```