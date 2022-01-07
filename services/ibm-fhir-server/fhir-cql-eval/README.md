# $cql/$evaluate extension

This directory contains a docker image that extends the IBM FHIR Server to allow cql evaluation either directly or via a Library resource.

# Bill of materials

* IBM FHIR Server
* fhir-operation-cqf
* fhir-operation-cpg

# How to use this extension

## Build it yourself

Using the included Dockerfile you can do a docker build/docker push to your own container registry.  Then update the health-patterns `values.yaml` to allow the fhir server to use this new container (add the following lines under the fhir server configurations)

```
fhir:
  name: fhir
  enabled: true
...
  image:
  # -- The repository to pull the IBM FHIR Server image from
    repository: <your repo>/<your container name>
  # -- IBM FHIR Server container image tag
    tag: "<your tag>"
```

## Use the prebuilt Alvearie container on Quay.io

A prebuilt container `quay.io/alvearie/fhir-cql` with tag `latest` has already been built and can be used directly.

Just add the following to your `values.yaml` file under the fhir server configurations

```
fhir:
  name: fhir
  enabled: true
...
  image:
  # -- The repository to pull the IBM FHIR Server image from
    repository: quay.io/alvearie/fhir-cql
  # -- IBM FHIR Server container image tag
    tag: "latest"
```

If you wish to write cql libraries that access other user created resources (such as including other cql libraries or accessing a valueSet), then it is necessary to enable the `serverRegistryResourceProvider`.  This can be done by simply adding the following to your `values.yaml` file under the fhir server configurations.

```
serverRegistryResourceProviderEnabled: true
```
