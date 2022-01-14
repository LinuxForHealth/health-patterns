#!/usr/bin/env python3

# Assist in the setup for Clinical Ingestion Flow
# Load processor group, set passwords, enable controllers

import requests
import sys
import time
import argparse
import urllib3

urllib3.disable_warnings()

debug = False # turn off debug by default

def main():
    fhir_password = "integrati0n"
    kafka_password = "integrati0n"
    addNLPInsights = False
    runASCVD = False
    deidentifyData = False
    resolveTerminology = False
    releaseName = ""
    deidConfigName = "default"
    deidPushToFhir = "True"
    runFHIRDataQuality = False

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseUrl", help="Base url for nifi instance")
    parser.add_argument("--fhir_pw", help="FHIR password")
    parser.add_argument("--kafka_pw", help="Kafka password")
    parser.add_argument("--addNLPInsights", help="Enable Add NLP Insights by default")
    parser.add_argument("--runASCVD", help="Enable ASCVD by default")
    parser.add_argument("--deidentifyData", help="Enable Deidentify Data by default")
    parser.add_argument("--resolveTerminology", help="Enable Terminology Services by default")
    parser.add_argument("--releaseName", help="Release Name")
    parser.add_argument("--deidConfigName", help="Deidentification Config Name")
    parser.add_argument("--deidPushToFhir", help="Boolean indicating deidentified data should be persisted")
    parser.add_argument("--runFHIRDataQuality", help="Enable FHIR data quality check")


    args = parser.parse_args()

    baseURL = args.baseUrl
    if args.fhir_pw:
        fhir_password = args.fhir_pw
    if args.kafka_pw:
        kafka_password = args.kafka_pw
    if args.addNLPInsights:
        addNLPInsights = args.addNLPInsights
    if args.runASCVD:
        runASCVD = args.runASCVD
    if args.deidentifyData:
        deidentifyData = args.deidentifyData
    if args.resolveTerminology:
        resolveTerminology = args.resolveTerminology
    if args.releaseName:
        releaseName = args.releaseName
    if args.deidConfigName:
        deidConfigName = args.deidConfigName
    if args.deidPushToFhir:
        deidPushToFhir = args.deidPushToFhir
    if args.runFHIRDataQuality:
        runFHIRDataQuality = args.runFHIRDataQuality

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
        print("BaseURL requires trailing /, fixing...")
        baseURL = baseURL + "/"  #add the trailing / if needed

    #Set specific passwords in the parameter contexts for fhir, kafka, and deid

    print("Updating parameter context parameters based on config...")
    updateParameters(baseURL, fhir_password, kafka_password, releaseName, addNLPInsights, runASCVD, deidentifyData, resolveTerminology, deidConfigName, deidPushToFhir, runFHIRDataQuality)
    print("Parameter update complete...\n")

    print("Finding all processor groups to update")
    finalGroupList = findProcessorGroups(baseURL)
    print("Done finding all processor groups...\n")

    #Enable all controller services that are currently disabled-starting from root
    print("Enabling all controller services...")
    enableControllerServices(baseURL, finalGroupList)
    print("Controller Services enabled...\n")

    #Start all of the processors in the process group that was added in step 1
    print("Starting all processors in the configured process group(s)")
    startAllProcessors(baseURL, finalGroupList)
    print("All processors in the configured processor group(s) started...\n")

    print("Start Health Patterns Flow complete")

def findProcessorGroups(baseURL):
    rootProcessGroupsURL = baseURL + "nifi-api/flow/process-groups/root"
    resp = requests.get(url=rootProcessGroupsURL, verify=False)
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
        resp = requests.get(url=pgURL, verify=False)
        groupDict = dict(resp.json())
        # add all first level subgroups
        for group in groupDict["processGroupFlow"]["flow"]["processGroups"]:
            groupList.append(group["id"])

    if debug:
        print(finalGroupList)

    return finalGroupList

def enableControllerServices(baseURL, finalGroupList):
    controllerServices = [] #hold the list of all controller services found in all process groups

    for agroup in finalGroupList:
        csURL = baseURL + "nifi-api/flow/process-groups/" + agroup + "/controller-services"
        resp = requests.get(url=csURL, verify=False)
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
        resp = requests.get(url=csURL, verify=False)
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

            resp = requests.put(url=enableURL, json=enableJson, verify=False)

            if debug:
                print(resp, resp.content)

def startAllProcessors(baseURL, finalGroupList):
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
        resp = requests.get(url=baseURL + status2GetEndpoint, verify=False)
        statusdict = dict(resp.json())
        stoppedcount = statusdict["stoppedCount"]
        if debug:
            print("Stopped Count: ", thegroup, "is ", int(stoppedcount))
        tries = 0
        while stoppedcount > 0 and tries < MAXRETRIES:  #there are still some processors that are not running so start again
            startupJson = {"id":thegroup,"state":"RUNNING"} #reschedule to running state
            startupPutEndpoint = "nifi-api/flow/process-groups/" + thegroup
            resp = requests.put(url=baseURL + startupPutEndpoint, json=startupJson, verify=False)
            tries = tries + 1  #we will only do this MAXTRIES times
            if debug:
                print(resp.content)
            if debug:
                print("Response from startup...", thegroup)
                print(resp)
                print(resp.content)

            time.sleep(1) #wait a bit for the process group to reset itself before getting next status

            status2GetEndpoint = "nifi-api/process-groups/" + thegroup
            resp = requests.get(url=baseURL + status2GetEndpoint, verify=False)
            statusdict = dict(resp.json())
            stoppedcount = statusdict["stoppedCount"]
            if debug:
                print("Stopped Count: ", thegroup, "is ", int(stoppedcount))

    if debug:
        for agroup in finalGroupList:
            status2GetEndpoint = "nifi-api/process-groups/" + agroup
            resp = requests.get(url=baseURL + status2GetEndpoint, verify=False)
            statusdict = dict(resp.json())
            stoppedcount = statusdict["stoppedCount"]
            print("Stopped Count: ", agroup, "is ", int(stoppedcount))

def updateParameters(baseURL, fhir_password, kafka_password, releaseName, addNLPInsights, runASCVD, deidentifyData, resolveTerminology, deidConfigName, deidPushToFhir, runFHIRDataQuality):
    #Get parameter contexts
    resp = requests.get(url=baseURL + "nifi-api/flow/parameter-contexts", verify=False)
    if debug:
        print(resp.content)

    contexts = dict(resp.json())["parameterContexts"]
    if debug:
        print("CONTEXTS:", contexts)

    for context in contexts:
        if "ingestion-parameter-context" in context["component"]["name"]:
            if debug:
                print("Processing ingestion-parameter-context")

            contextId = context["id"]
            if debug:
                print("FHIR context:", contextId)

            update_parameter(baseURL, contextId, "FHIR_URL_PatientAccess", "http://" + releaseName + "-fhir/fhir-server/api/v4", False)
            update_parameter(baseURL, contextId, "FHIR_URL_ProviderDirectory", "http://" + releaseName + "-fhir/fhir-server/api/v4", False)
            update_parameter(baseURL, contextId, "FHIR_UserPwd_PatientAccess", fhir_password, True)
            update_parameter(baseURL, contextId, "FHIR_UserPwd_ProviderDirectory", fhir_password, True)
            update_parameter(baseURL, contextId, "kafka.auth.password", kafka_password, True)
            update_parameter(baseURL, contextId, "kafka.brokers", releaseName + "-kafka:9092", False)
            update_parameter(baseURL, contextId, "HL7_RESOURCE_GENERATOR_URL", "http://" + releaseName + "-hl7-resource-generator:8080/hl7/transformation", False)
            update_parameter(baseURL, contextId, "RUN_FHIR_DATA_QUALITY_URL", "http://" + releaseName + "-fhir-data-quality:5000", False)
            update_parameter(baseURL, contextId, "RunFHIRDataQuality", runFHIRDataQuality)

        if "enrichment-parameter-context" in context["component"]["name"]:
            if debug:
                print("Processing enrichment-parameter-context")

            contextId = context["id"]
            if debug:
                print("Enrichment context: ", contextId)

            update_parameter(baseURL, contextId, "kafka.auth.password", kafka_password, True)
            update_parameter(baseURL, contextId, "kafka.brokers", releaseName + "-kafka:9092", False)
            update_parameter(baseURL, contextId, "DEID_PREP_URL", "http://" + releaseName + "-deid-prep:8080", False)
            update_parameter(baseURL, contextId, "TERM_SERVICES_PREP_URL", "http://" + releaseName + "-term-services-prep:8080", False)
            update_parameter(baseURL, contextId, "ADD_NLP_INSIGHTS_URL", "http://" + releaseName + "-nlp-insights:5000", False)
            update_parameter(baseURL, contextId, "AddNLPInsights", addNLPInsights)
            update_parameter(baseURL, contextId, "RunASCVD", runASCVD)
            update_parameter(baseURL, contextId, "DeidentifyData", deidentifyData)
            update_parameter(baseURL, contextId, "ResolveTerminology", resolveTerminology)
            update_parameter(baseURL, contextId, "DEID_CONFIG_NAME", deidConfigName)
            update_parameter(baseURL, contextId, "DEID_PUSH_TO_FHIR", deidPushToFhir)
            update_parameter(baseURL, contextId, "ASCVD_FROM_FHIR_URL", "http://" + releaseName + "-ascvd-from-fhir:5000", False)


def update_parameter(baseURL, contextId, name, value, sensitive=False):
    # Updates a parameter in the given context and polls the request for completion
    # Finally, the request is deleted

    versionNum = 0
    createPostEndpoint = "nifi-api/parameter-contexts/" + contextId + "/update-requests"
    # Don't know what the current version is, so loop through until you find the "latest" version and update it
    while(True):
        parameterJson = {"revision": {"version": versionNum}, "id": contextId, "component": {
            "parameters": [{"parameter": {"name": name, "sensitive": sensitive, "value": value}}],
            "id": contextId}}
        resp = requests.post(url=baseURL + createPostEndpoint, json=parameterJson, verify=False)
        if (resp.status_code==200):
            break
        versionNum += 1

    if debug:
        print(resp, resp.content)

    requestId = dict(resp.json())["request"]["requestId"]
    if debug:
        print(requestId)
    resp = requests.get(url=baseURL + createPostEndpoint + "/" + requestId, verify=False)
    if debug:
        print(resp, resp.content)

    complete = dict(resp.json())["request"]["complete"]
    if debug:
        print("update request status", name, complete)
    while str(complete) != "True":
        if debug:
            print("task not complete", name)

        resp = requests.get(url=baseURL + createPostEndpoint + "/" + requestId, verify=False)
        if debug:
            print(resp, resp.content)

        complete = dict(resp.json())["request"]["complete"]
        if debug:
            print("update request status", name, complete)

    if debug:
        print("Deleting the update task", name)
    resp = requests.delete(url=baseURL + createPostEndpoint + "/" + requestId, verify=False)

if __name__ == '__main__':
    main()
