#!/usr/bin/env python3

# Assist in the setup for Clinical Ingestion Flow
# Load processor group, set passwords, enable controllers

import requests
import sys
import time

import argparse

debug = False  # turn off debug by default

def main():
    regName = "default"  #default registry to use
    bucketName = "Health_Patterns"  #default bucket to use
    version = None #will search for latest version unless explicity set
    flowName = "Clinical Ingestion"  #assume that we want clinical ingestion flow for now
    x_pos = 0 # Specify an x position to place this component
    y_pos = 0 # Specify an y position to place this component

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseUrl", help="Base url for nifi instance")
    parser.add_argument("--reg", help="Registry")
    parser.add_argument("--bucket", help="Bucket")
    parser.add_argument("--flowName", help="Flow Name")
    parser.add_argument("--version", help="Version")
    parser.add_argument("--x", help="Horizontal position to place new component")
    parser.add_argument("--y", help="Vertical position to place new component")

    args = parser.parse_args()
    if args.reg:
        regName = args.reg
    if args.bucket:
        bucketName = args.bucket
    if args.version:
        version = int(args.version)
    if args.flowName:
        flowName = args.flowName
    if args.x:
        x_pos = args.x
    if args.y:
        y_pos = args.y_pos

    baseURL = args.baseUrl

    if debug:
        print([regName, bucketName, version])

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
        print("BaseURL requires trailing /, fixing...")
        baseURL = baseURL + "/"  #add the trailing / if needed

    print("Configuring with Nifi at BaseURL: ", baseURL)

    # Find the desired flow and place it on the root canvas

    # If found, the flowURL will be used to get the versions so that the latest
    # version is placed on the canvas.  Need to know the registry, bucket, and flow for the
    # desired flow name

    print("Creating process group...")

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
    #unless version is not None because then version already provided explicitly
    if version == None:
        versionURL = flowURL + "/" + theFlow + "/" + "versions"
        resp = requests.get(url=versionURL)
        if debug:
            print(dict(resp.json()))
        versionDict = dict(resp.json())

        version = 0
        for v in versionDict["versionedFlowSnapshotMetadataSet"]:
            aVersion = int(v["versionedFlowSnapshotMetadata"]["version"])
            if aVersion  > version:
                version = aVersion
        if debug:
            print("FOUND Version: ", version)

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

    createJson = {"revision":{"version":0},"component":{"versionControlInformation":{"registryId":theRegistry,"bucketId":theBucket,"flowId":theFlow,"version":version},"position":{"x":x_pos,"y":y_pos}}}
    createPostEndpoint = "nifi-api/process-groups/" + rootId + "/process-groups"
    resp = requests.post(url=baseURL + createPostEndpoint, json=createJson)
    if debug:
        print("Response from new group...")
        print(resp.content)
    newgroupid = (dict(resp.json()))["id"]
    if debug:
        print("New process group id...",newgroupid)
    print("Process group created...")

if __name__ == '__main__':
    main()
