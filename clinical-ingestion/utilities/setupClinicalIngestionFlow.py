#!/usr/bin/env python3

# Assist in the setup for Clinical Ingestion Flow
# Load processor group, set passwords, enable controllers

import requests
import sys
import time

import argparse

debug = False  # turn off debug by default

def main():
    regName = "default"  #default registry to use for clinical ingestion
    bucketName = "Health_Patterns"  #default bucket to use for clinical ingestion
    latest = None #will search for latest version unless explicity set

    enregName = "default" #default registry to use for enrichment
    enbucketName = "Health_Patterns" #default bucket to use for enrichment
    enlatest = None #will search for latest version unless explicity set

    parser = argparse.ArgumentParser()
    parser.add_argument("baseurl", help="Base url for nifi instance")
    parser.add_argument("pw", help="Clinical Ingestion default password")

    parser.add_argument("--cireg", help="Clinical Ingestion registry")
    parser.add_argument("--cibucket", help="Clinical Ingestion bucket")
    parser.add_argument("--civersion", help="Clinical Ingestion version")
    parser.add_argument("--enreg", help="Enrichment registry")
    parser.add_argument("--enbucket", help="Enrichment bucket")
    parser.add_argument("--enversion", help="Enrichment version")

    args = parser.parse_args()
    if args.cireg:
        regName = args.cireg
    if args.cibucket:
        bucketName = args.cibucket
    if args.civersion:
        latest = int(args.civersion)
    if args.enreg:
        enregName = args.enreg
    if args.enbucket:
        enbucketName = args.enbucket
    if args.enversion:
        enlatest = int(args.enversion)

    baseURL = args.baseurl
    defaultPWD = args.pw

    # set up configuration for each flow
    flowNames = ["Clinical Ingestion", "FHIR Bundle Enrichment"]
    flowConfig = {}
    flowConfig[flowNames[0]] = [regName, bucketName, latest]
    flowConfig[flowNames[1]] = [enregName, enbucketName, enlatest]

    if debug:
        print(flowConfig)
    if debug:
        print(defaultPWD)

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
        print("BaseURL requires trailing /, fixing...")
        baseURL = baseURL + "/"  #add the trailing / if needed

    print("Configuring with Nifi at BaseURL: ", baseURL)

    # STEP 1: find the desired flow and place it on the root canvas

    # If found, the flowURL will be used to get the versions so that the latest
    # version is placed on the canvas.  Need to know the registry, bucket, and flow for the
    # desired flow name

    # This will be done for all configured flows

    for aflow in flowNames:

        print("Step 1: Creating process group...", aflow)

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
        registryname = flowConfig[aflow][0]
        regFound = False
        for regs in respDict["registries"]:
            if debug:
                print(regs)
            if regs["registry"]["name"] == registryname:
               regId = regs["registry"]["id"]
               regFound = True
               if debug:
                  print("FOUND Registry", registryname, "-->",regId)
               break

        if not regFound:
            print("script failed-no matching registry found:", registryname)
            exit(1)  #if we don't find the specific registry then we are done

        #search for bucket
        registrybucketname = flowConfig[aflow][1]
        bucketFound = False
        buckURL = regURL + "/" + regId + "/buckets"
        resp = requests.get(url=buckURL)
        if debug:
            print(dict(resp.json()))
        bucketDict = dict(resp.json())
        for bucket in bucketDict["buckets"]:
            if debug:
                print(bucket)
            if bucket["bucket"]["name"] == registrybucketname:
                bucketId = bucket['id']
                bucketFound = True
                if debug:
                    print("FOUND Bucket ", registrybucketname, "-->", bucketId)
                break

        if not bucketFound:
            print("script failed-no matching bucket found:", registrybucketname)
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
            if flow["versionedFlow"]["flowName"] == aflow:
                flowFound = True
                theRegistry = regId
                theBucket = bucketId
                theFlow = flow["versionedFlow"]["flowId"]
                if debug:
                    print("FOUND Flow: ", aflow, "-->", theFlow)
                break

        if not flowFound:
            print("script failed-no matching flow found:", aflow)
            exit(1)  #if we don't find the specific bucket then we are done

        #found the flow so now go ahead and find the latest version
        #unless latest is not None because then version already provided explicitly
        latest = None
        if flowConfig[aflow][2] == None:
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
            if debug:
                print("FOUND Version: ", latest)
        else:
            latest = flowConfig[aflow][2]

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
            print("Response from new group...")
            print(resp.content)
        newgroupid = (dict(resp.json()))["id"]
        if debug:
            print("New process group id...",newgroupid)
        print("Step 1 complete: Process group created...", aflow)


    #STEP 2: Set specific passwords in the parameter contexts for fhir, kafka, and deid

    print("Step 2: Setting default password in all parameter contexts...")

    #Get parameter contexts
    resp = requests.get(url=baseURL + "nifi-api/flow/parameter-contexts")
    if debug:
        print(resp.content)

    contexts = dict(resp.json())["parameterContexts"]
    if debug:
        print("CONTEXTS:", contexts)

    for context in contexts:
        if "cms_adapter_parameters" in context["component"]["name"]:
            if debug:
                print("processing new cms_adapter_parameters")
            #setting the fhir and kafka passwords
            contextId = context["id"]
            if debug:
                print("FHIR context:", contextId)

            updatePwd(baseURL, contextId, 0, "FHIR_UserPwd_PatientAccess", defaultPWD)
            updatePwd(baseURL, contextId, 1, "FHIR_UserPwd_ProviderDirectory", defaultPWD)
            updatePwd(baseURL, contextId, 2, "kafka.auth.password", defaultPWD)

        if "De-Identification" in context["component"]["name"]:
            if debug:
                print("processing deid")
            #set deid passwords
            contextId = context["id"]
            if debug:
                print("DeId context: ", contextId)

            updatePwd(baseURL, contextId, 0, "DEID_FHIR_PASSWORD", defaultPWD)

        if "Enrichment" in context["component"]["name"]:
            if debug:
                print("processing enrichment")
            #set deid passwords
            contextId = context["id"]
            if debug:
                print("Enrichment context: ", contextId)

            updatePwd(baseURL, contextId, 0, "kafka.auth.password", defaultPWD)

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

    # STEP 4: start all of the processors in the process group that was added in step 1

    print("Step 4: Start all processors in the new process group")

    if debug:
        print("Original ordering....")
        print(finalGroupList)

    finalGroupList.reverse()

    if debug:
        print("Reordering, starting from bottom up....")
        print(finalGroupList)

    MAXRETRIES = 5
    for thegroup in finalGroupList:
        status2GetEndpoint = "nifi-api/process-groups/" + thegroup
        resp = requests.get(url=baseURL + status2GetEndpoint)
        statusdict = dict(resp.json())
        stoppedcount = statusdict["stoppedCount"]
        if debug:
            print("Stopped Count: ", thegroup, "is ", int(stoppedcount))
        tries = 0
        while stoppedcount > 0 and tries < MAXRETRIES:  #there are still some processors that are not running so start again
            startupJson = {"id":thegroup,"state":"RUNNING"} #reschedule to running state
            startupPutEndpoint = "nifi-api/flow/process-groups/" + thegroup
            resp = requests.put(url=baseURL + startupPutEndpoint, json=startupJson)
            tries = tries + 1  #we will only do this MAXTRIES times
            if debug:
                print(resp.content)
            if debug:
                print("Response from startup...", thegroup)
                print(resp)
                print(resp.content)

            time.sleep(1) #wait a bit for the process group to reset itself before getting next status

            status2GetEndpoint = "nifi-api/process-groups/" + thegroup
            resp = requests.get(url=baseURL + status2GetEndpoint)
            statusdict = dict(resp.json())
            stoppedcount = statusdict["stoppedCount"]
            if debug:
                print("Stopped Count: ", thegroup, "is ", int(stoppedcount))

    if debug:
        for agroup in finalGroupList:
            status2GetEndpoint = "nifi-api/process-groups/" + agroup
            resp = requests.get(url=baseURL + status2GetEndpoint)
            statusdict = dict(resp.json())
            stoppedcount = statusdict["stoppedCount"]
            print("Stopped Count: ", agroup, "is ", int(stoppedcount))

    print("Step 4 complete: All processors in new processor group started....")

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
