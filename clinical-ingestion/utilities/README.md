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
1. Load the Enrichment Flow processor group onto the Nifi canvas
1. Set the missing passwords in the parameter contexts described above
1. Enable the controller services described above

Prerequisites
  - Python 3 installed
  - The `requests` module must be installed (`pip install requests`)
  - Change the permissions on the script to add executable (`chmod +x setupClinicalIngestionFlow.py`)

In order to execute the script, two positional arguments must be provided.  
  1. The base URL for the Nifi instance including the port.
  1. The default password to be used.  The script assumes that all passwords will be set to the same default.

For example, from the `utilities` directory, run

`./setupClinicalIngestionFlow <<Nifi Server:Nifi Port>> <<default password>>`

If your Nifi server was running on `http://nifi.xyz.org:8080` and you want the default password to be `twinkle`, then it would be

`./setupClinicalIngestionFlow http://nifi.xyz.org:8080  twinkle`

The script currently assumes the flow will come from the `default` registry and use the latest
version available.  A set of optional arguments allow the user to specify a registry,
bucket, and version for each flow.  These can be seen using the -h option.

`./setupClinicalIngestionFlow.py -h`
```
usage: setupClinicalIngestionFlow.py [-h] [--cireg CIREG] [--cibucket CIBUCKET] [--civersion CIVERSION] [--enreg ENREG]
                                     [--enbucket ENBUCKET] [--enversion ENVERSION]
                                     baseurl pw

positional arguments:
  baseurl               Base url for nifi instance
  pw                    Clinical Ingestion default password

optional arguments:
  -h, --help            show this help message and exit
  --cireg CIREG         Clinical Ingestion registry
  --cibucket CIBUCKET   Clinical Ingestion bucket
  --civersion CIVERSION Clinical Ingestion version
  --enreg ENREG         Enrichment registry
  --enbucket ENBUCKET   Enrichment bucket
  --enversion ENVERSION Enrichment version
```
 
Status messages will log the activity of the script and you will see a completion message at the end.  At that point, you may need to refresh your Nifi canvas to see the new process group.
