<p align="center">
    <a href="https://github.com/Alvearie">
        <img src="https://avatars.githubusercontent.com/u/72946463?s=200&v=4" height="100" alt="Alvearie">
    </a>
</p>


<p align="center">
    <a href="https://www.ibm.com/developerworks/learn/java/">
    <img src="https://img.shields.io/badge/platform-java-lightgrey.svg?style=flat" alt="platform">
    </a>
    <img src="https://img.shields.io/badge/license-Apache2-blue.svg?style=flat" alt="Apache 2">
</p>


# DeID Service

TBD

## Steps

You can [deploy this application to Kubernetes](#deploying-to-kubernetes) or [build it locally](#building-locally) by cloning this repo first.

### Deploying to Kubernetes

Run:

1. `git clone https://github.com/Alvearie/health-patterns.git`
1. `cd clinical-ingestion/cohort-service`
1. `kubectl apply -f manifests/kube.deploy.yaml`

### Building Locally

#### Pre-Requisites

* [Maven](https://maven.apache.org/install.html)
* Java 8: Any compliant JVM should work.
  * [Java 8 JDK from Oracle](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
  * [Java 8 JDK from IBM (AIX, Linux, z/OS, IBM i)](http://www.ibm.com/developerworks/java/jdk/),
    or [Download a Liberty server package](https://developer.ibm.com/assets/wasdev/#filter/assetTypeFilters=PRODUCT)
    that contains the IBM JDK (Windows, Linux)

As mentioned above, this project depends on the [quality-measure-and-cohort-service](https://github.com/Alvearie/quality-measure-and-cohort-service), so please follow the [getting started](https://github.com/Alvearie/quality-measure-and-cohort-service/blob/main/docs/dev-guide/getting-started.md) instructions for extracting and building that project. 

#### Building

1. `git clone https://github.com/Alvearie/health-patterns.git`
1. `cd clinical-ingestion/cohort-service`
1. `maven install`
1. `java -jar ./target/cohort-service-{version}.jar`


To run an application in Docker use the Docker file called `Dockerfile`. If you do not want to install Maven locally you can use `Dockerfile-tools` to build a container with Maven installed.

## License

This application is licensed under the Apache License, Version 2. Separate third-party code objects invoked within this code pattern are licensed by their respective providers pursuant to their own separate licenses. Contributions are subject to the [Developer Certificate of Origin, Version 1.1](https://developercertificate.org/) and the [Apache License, Version 2](https://www.apache.org/licenses/LICENSE-2.0.txt).

[Apache License FAQ](https://www.apache.org/foundation/license-faq.html#WhatDoesItMEAN)
