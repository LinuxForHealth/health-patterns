#!/usr/bin/env python3

# Assist in the setup for Clinical Ingestion Flow
# Load processor group, set passwords, enable controllers

import requests
import sys

debug = False  # turn off debug by default

def main():
    regName = "default"  #default registry to use
    bucketName = "Health_Patterns"  #default bucket to use

    if len(sys.argv) < 3:
        print("Must include base url and default password as arguments")
        print("USAGE: setupFlow.py URL defaultpassword")
        exit(1)  #need to retry

    baseURL = sys.argv[1]
    defaultPWD = sys.argv[2]

    #now handle optional registry and bucket
    if len(sys.argv) == 4: #included registry name
        regName = sys.argv[3]
    if len(sys.argv) == 5: #included registry name and bucket name
        regName = sys.argv[3]
        bucketName = sys.argv[4]

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
        print("BaseURL requires trailing /, fixing...")
        baseURL = baseURL + "/"  #add the trailing / if needed

    print("Configuring with Nifi at BaseURL: ", baseURL)

    flowName = "Clinical Ingestion"  #assume that we want clinical ingestion flow for now

    # STEP 1: find the desired flow and place it on the root canvas

    # If found, the flowURL will be used to get the versions so that the latest
    # version is placed on the canvas.  Need to know the registry, bucket, and flow for the
    # desired flow name

    print("Step 1: Creating process group...")

    found = False
    flowURL = None
    theRegistry = None
    theBucket = None
    theFlow = None

    regURL = baseURL + "nifi-api/flow/registries"
    resp = requests.get(url=regURL)
    if debug:
        print(dict(resp.json()))
    respDict = dict(resp.json())

    #search for registry
    regFound = False
    for regs in respDict["registries"]:
        if debug:
            print(regs)
        if regs["registry"]["name"] == regName:
           regId = regs["registry"]["id"]
           regFound = True
           if debug:
              print("FOUND Registry", regName, "-->",regId)
           break

    if not regFound:
        print("script failed-no matching registry found:", regName)
        exit(1)  #if we don't find the specific registry then we are done

    #search for bucket
    bucketFound = False
    buckURL = regURL + "/" + regId + "/buckets"
    resp = requests.get(url=buckURL)
    if debug:
        print(dict(resp.json()))
    bucketDict = dict(resp.json())
    for bucket in bucketDict["buckets"]:
        if debug:
            print(bucket)
        if bucket["bucket"]["name"] == bucketName:
            bucketId = bucket['id']
            bucketFound = True
            if debug:
                print("FOUND Bucket ", bucketName, "-->", bucketId)
            break

    if not bucketFound:
        print("script failed-no matching bucket found:", bucketName)
        exit(1)  #if we don't find the specific bucket then we are done

    #search for flow
    flowFound = False
    flowURL = buckURL + "/" + bucketId + "/" + "flows"
    resp = requests.get(url=flowURL)
    if debug:
        print(dict(resp.json()))
    flowDict = dict(resp.json())
    for flow in flowDict["versionedFlows"]:
        if debug:
            print(flow)
        if flow["versionedFlow"]["flowName"] == flowName:
            flowFound = True
            theRegistry = regId
            theBucket = bucketId
            theFlow = flow["versionedFlow"]["flowId"]
            if debug:
                print("FOUND Flow: ", flowName, "-->", theFlow)
            break

    if not flowFound:
        print("script failed-no matching flow found:", flowName)
        exit(1)  #if we don't find the specific bucket then we are done

    #found the flow so now go ahead and find the latest version

    versionURL = flowURL + "/" + theFlow + "/" + "versions"
    resp = requests.get(url=versionURL)
    if debug:
        print(dict(resp.json()))
    versionDict = dict(resp.json())

    latest = 0
    for v in versionDict["versionedFlowSnapshotMetadataSet"]:
        version = int(v["versionedFlowSnapshotMetadata"]["version"])
        if version > latest:
            latest = version

    #Get root id for canvas process group

    URL = baseURL + "nifi-api/flow/process-groups/root"
    resp = requests.get(url=URL)
    if debug:
        print(resp)
        print(resp.content)
    rootId = (dict(resp.json()))["processGroupFlow"]["id"]
    if debug:
        print(rootId)

    #Create new process group from repo

    createJson = {"revision":{"version":0},"component":{"versionControlInformation":{"registryId":theRegistry,"bucketId":theBucket,"flowId":theFlow,"version":latest}}}
    createPostEndpoint = "nifi-api/process-groups/" + rootId + "/process-groups"
    resp = requests.post(url=baseURL + createPostEndpoint, json=createJson)
    if debug:
        print(resp.content)

    print("Step 1 complete: Process group created...")

    #STEP 2: Set specific passwords in the parameter contexts for fhir, kafka, and deid

    print("Step 2: Setting default password in all parameter contexts...")

    #Get parameter contexts
    resp = requests.get(url=baseURL + "nifi-api/flow/parameter-contexts")
    if debug:
        print(resp.content)

    contexts = dict(resp.json())["parameterContexts"]
    if debug:
        print(contexts)

    for context in contexts:
        if "FHIR" in context["component"]["name"]:
            if debug:
                print("processing fhir")
            #setting the fhir password
            contextId = context["id"]
            if debug:
                print("FHIR context:", contextId)

            updatePwd(baseURL, contextId, 0, "FHIR_PASSWORD", defaultPWD)

        if "Kafka" in context["component"]["name"]:
            if debug:
                print("processing kafka-two pwds")

            #set kafka passwords
            contextId = context["id"]
            if debug:
                print("Kafka context: ", contextId)

            updatePwd(baseURL, contextId, 0, "kafka.auth.password", defaultPWD)

        if "De-Identification" in context["component"]["name"]:
            if debug:
                print("processing deid-two pwds")
            #set deid passwords
            contextId = context["id"]
            if debug:
                print("DeId context: ", contextId)

            updatePwd(baseURL, contextId, 0, "DEID_FHIR_PASSWORD", defaultPWD)

    print("Step 2 complete: Password set complete...")

    #STEP 3: Enable all controller services that are currently disabled-starting from root

    print("Step 3: Enabling all controller services...")

    rootProcessGroupsURL = baseURL + "nifi-api/flow/process-groups/root"
    resp = requests.get(url=rootProcessGroupsURL)
    if debug:
        print(resp, resp.content)

    groupDict = dict(resp.json())

    groupList = []
    finalGroupList = []

    # start with the root groups
    for group in groupDict["processGroupFlow"]["flow"]["processGroups"]:
        if debug:
            print(group["id"])
        groupList.append(group["id"])

    if debug:
        print("GROUPLIST=", groupList)
    while len(groupList) > 0:
        #more groups to try
        nextGroup = groupList.pop(0)
        finalGroupList.append(nextGroup)
        pgURL = baseURL + "nifi-api/flow/process-groups/" + nextGroup
        resp = requests.get(url=pgURL)
        groupDict = dict(resp.json())
        # add all first level subgroups
        for group in groupDict["processGroupFlow"]["flow"]["processGroups"]:
            groupList.append(group["id"])

    if debug:
        print(finalGroupList)

    controllerServices = [] #hold the list of all controller services found in all process groups

    for agroup in finalGroupList:
        csURL = baseURL + "nifi-api/flow/process-groups/" + agroup + "/controller-services"
        resp = requests.get(url=csURL)
        if debug:
            print(resp, resp.content)
        csDict = dict(resp.json())

        for service in csDict["controllerServices"]:
            serviceId = service["id"]
            if serviceId not in controllerServices:
                controllerServices.append(serviceId)

    if debug:
        print(controllerServices)

    for cs in controllerServices:
        csURL = baseURL + "nifi-api/controller-services/" + cs
        resp = requests.get(url=csURL)
        if debug:
            print("CS=", cs)
            print(resp, resp.content)
        csDict = dict(resp.json())
        currentState = csDict["component"]["state"]
        if debug:
            print(cs, currentState)

        if currentState == "DISABLED": #enable all services that are currently disabled
            enableJson = {"revision": {"version": 0}, "state": "ENABLED"}
            enableURL = baseURL + "nifi-api/controller-services/" + cs + "/run-status"

            resp = requests.put(url=enableURL, json=enableJson)

            if debug:
                print(resp, resp.content)

    print("Step 3 complete: Controllers enabled...")
    print("Setup task complete")

def updatePwd(baseURL, contextId, versionNum, pwdName, pwdValue):
    # Updates the password and polls the request for completion
    # Finally, the request is deleted

    passwordJson = {"revision": {"version": versionNum}, "id": contextId, "component": {
        "parameters": [{"parameter": {"name": pwdName, "sensitive": "true", "value": pwdValue}}],
        "id": contextId}}
    createPostEndpoint = "nifi-api/parameter-contexts/" + contextId + "/update-requests"
    resp = requests.post(url=baseURL + createPostEndpoint, json=passwordJson)
    if debug:
        print(resp, resp.content)

    requestId = dict(resp.json())["request"]["requestId"]
    if debug:
        print(requestId)
    resp = requests.get(url=baseURL + createPostEndpoint + "/" + requestId)
    if debug:
        print(resp, resp.content)

    complete = dict(resp.json())["request"]["complete"]
    if debug:
        print("update request status", pwdName, complete)
    while str(complete) != "True":
        if debug:
            print("task not complete", pwdName)

        resp = requests.get(url=baseURL + createPostEndpoint + "/" + requestId)
        if debug:
            print(resp, resp.content)

        complete = dict(resp.json())["request"]["complete"]
        if debug:
            print("update request status", pwdName, complete)

    if debug:
        print("Deleting the update task", pwdName)
    resp = requests.delete(url=baseURL + createPostEndpoint + "/" + requestId)

if __name__ == '__main__':
    main()
