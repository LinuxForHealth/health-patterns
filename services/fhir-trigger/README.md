# fhir-trigger service

A deployable service that will respond to either fhir
notifications or fhir history events (not both at the same time).
For any fhir notification or history event, the service will
- find the patient id
- build a custom resource bundle for that patient
- post that bundle to a preconfigured kafka topic for
further downstream processing



