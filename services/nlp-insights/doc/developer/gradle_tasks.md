# Gradle Tasks

In the root directory of the project repo, there are two wrapper commands for executing gradle tasks.

* gradlew (linux)
* gradlew.bat (windows)

These commands will download (if necessary) the correct version of gradle for you and use it for task execution.

Tasks always run dependent tasks, so for example a 'test' task will also build the python wheel before running unit tests on the wheel. A dockerRun task will first execute the docker task to build the docker image, unless the image is current.

A summary of the most useful tasks is included here.


Type | Task | Description
---- | --- | ----
General | &nbsp; | &nbsp;
 &nbsp; | tasks | list tasks and include descriptions
Build |&nbsp; | &nbsp;
&nbsp; | clean | deletes build artifacts
&nbsp; | install | builds a python wheel and installs it to the build's virtual environment.
Docker |&nbsp; |  &nbsp;
&nbsp; | docker | builds a docker image
&nbsp; | dockerRun | starts a docker container for the nlp-insights service
&nbsp; | dockerPush | pushes the docker image to a container repository
&nbsp; | dockerStop | stops the container if it is running
&nbsp; | dockerRemoveContainer | removes the container from the registery
Quality | &nbsp; | &nbsp;
&nbsp; | checkSource | runs unit tests, doc tests and linters
&nbsp; | test | runs unit tests and doc tests

The `gradle.properties` file defines default build properties. Most of these will not need to change, however the version number will be updated and is used for:
* Component of the docker image tag. (The tag corresponds to the version used for the helm charts in `values.yaml`)
* Version of the python wheel (Currently the wheel is not published anywhere)
