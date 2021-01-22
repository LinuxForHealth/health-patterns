# Alvearie NiFi Custom Processors Container

This container includes the Alvearie Ingestion custom NiFi processors. It does not contain any executables, it is simply meant to be mounted as a custom processor directory in an NiFi installation.

The container can be downloaded from Dockher Hub here: [alvearie/nars](https://hub.docker.com/repository/docker/alvearie/nars).


### Building Alvearie NAR container

To rebuild the alvearie/nars container, run the following command: 

- `docker build -t alvearie/nars:0.0.1 .`

Following this, you can push the container using this command:

- `docker push alvearie/nars:0.0.1`