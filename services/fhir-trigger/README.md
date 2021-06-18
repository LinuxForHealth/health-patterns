# fhir-trigger service

A deployable service that will respond to either fhir
notifications or fhir history events (not both at the same time).
For any fhir notification or history event, the service will
- find the patient id
- build a custom resource bundle for that patient
- post that bundle to a preconfigured kafka topic for
further downstream processing

### Configuration environment variables

### Required for all configurations

#### TRIGGERTYPE
    Configure which type of trigger will be used
    Required: must be history or notification

#### RESOURCESLIST
    A space delimited string containing the names of resources
    that will be included in the custom bundle
    Example: "Patient Observation Condition"
#### KAFKAUSER
    The predefined kafka username (token is the default)
    Example: "token"
#### KAFKAPW
    The password for the kafka user as defined in the fhir
    notifications configuration
    Example: "mypasswd"
#### KAFKABOOTSTRAP
    The internal name and port for the kafka broker
    Example: "ingestion-kafka:9092"
#### PRODUCERTOPIC
    The kafka topic where the custom fhir bundles will be posted
    Example: "new.bundle.out"
#### FHIRENDPOINT
    The complete public or internal name of the fhir server base
    Example: "http://ingestion-fhir/fhir-server/api/v4"
#### FHIRUSERNAME
    The fhir user name configured on the fhir server
    Example: "fhiruser"
#### FHIRPW
    The password for fhirusername
    Example: "fhirpw"
###Required for notification
#### MAXITERATIONS
    A count down limit for waiting for notifications for the
    same patient
    Example: "15"
#### ALARMMINUTES
    Sets a maximum timer so that constant notifications for a single
    patient do not cause prolonged waiting.
    Example: "10"
#### CONSUMERTOPIC
    The kafka topic configured in the fhir server for fhir notifications
    Example: "fhir.notification"
### Required for history
#### CHUNKSIZE
    The number of history events to take as a whole when searching
    for patient ids.  Any value greater than 1000 will return
    no more than 1000 resources.
    Example: "200"
#### SLEEPSECONDS
    How long to wait before getting the next chunk of history
    events.
    Example: "60"

