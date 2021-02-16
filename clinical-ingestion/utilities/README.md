# Utilities

This directory contains various utilities that are used to automate the installation of the Alvearie Health Patterns Clinical Ingestion chart.
The utilities included here are built into a container and loaded as a sidecar container next to some of the containers in the Alvearie Ingestion chart.

The container image used to load these utilities is built on top of an image that includes various networking utilities, and python.
To build and push it simply:

```
cd health-patterns/clinical-ingestion/utilities
docker build -t alvearie/nifi-setup:{tag} .
docker push alvearie/nifi-setup:{tag}
```

### wait-for-nifi.sh

This script waits for a NiFi server running on this host to fully initialize.

### initialize-reporting-task.sh

This script creates, configures, and starts a prometheus reporting task for generating metrics to be used in grafana dashboards.

### setupClinicalIngestionFlow.py

To assist with the Clinical Ingestion Flow configuration, a Python script (utilities/setupClinicalIngestionFlow.py) will automate the steps necessary to use the Clinical Ingestion Flow.  The script will

1. Load the Clinical Ingestion Flow processor group onto the Nifi canvas
1. Set the missing passwords in the parameter contexts described above
1. Enable the controller services described above

Prerequisites
  - Python 3 installed
  - The `requests` module must be installed (`pip install requests`)
  - Change the permissions on the script to add executable (`chmod +x setupClinicalIngestionFlow.py`)
  
In order to execute the script, two arguments must be provided.  
  1. The base URL for the Nifi instance including the port.
  1. The default password to be used.  The script assumes that all passwords will be set to the same default.
  
For example, from the `utilities` directory, run

`./setupClinicalIngestionFlow <<Nifi Server:Nifi Port>> <<default password>>`

If your Nifi server was running on `http://nifi.xyz.org:8080` and you want the default password to be `twinkle`, then it would be

`./setupClinicalIngestionFlow http://nifi.xyz.org:8080  twinkle`

The script currently assumes the flow will come from the `default` registry.  An optional 3rd argument allows the developer to change that registry to a custom value.

`./setupClinicalIngestionFlow http://nifi.xyz.org:8080  twinkle someotherregistry`

In addition, you can also provide a registry and a bucket.  Note: if you want to provide a bucket name, you are **required** to also specify a registry name that contains that bucket.  For example

`./setupClinicalIngestionFlow http://nifi.xyz.org:8080  twinkle registryname bucketname`

Status messages will log the activity of the script and you will see a completion message at the end.  At that point, you may need to refresh your Nifi canvas to see the new process group.