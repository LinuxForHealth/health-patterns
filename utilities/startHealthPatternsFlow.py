#!/usr/bin/env python3

# Assist in the setup for Clinical Ingestion Flow
# Load processor group, set passwords, enable controllers

import requests
import sys
import time

import argparse

debug = False  # turn off debug by default

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseUrl", help="Base url for nifi instance")
    parser.add_argument("--pw", help="default password")

    args = parser.parse_args()

    baseURL = args.baseUrl
    defaultPWD = args.pw

    if debug:
        print(defaultPWD)

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
        print("BaseURL requires trailing /, fixing...")
        baseURL = baseURL + "/"  #add the trailing / if needed

    print("Configuring with Nifi at BaseURL: ", baseURL)

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
