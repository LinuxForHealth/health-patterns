#!/usr/bin/env python3

# Check to see if any processor groups are already loaded and return "deployed" if processor groups 
# are detected. This will help to prevent re-deploying when persistence is enabled.

import requests
import sys
import time
import argparse
import urllib3

urllib3.disable_warnings()

def main():
    bearerToken = None

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseUrl", help="Base url for nifi instance")
    parser.add_argument("--bearerToken", help="Bearer Token to make API calls")

    args = parser.parse_args()

    baseURL = args.baseUrl
    bearerToken = args.bearerToken

    #now fix trailing / problem if needed
    if baseURL[-1] != "/":
      print("BaseURL requires trailing /, fixing...")
      baseURL = baseURL + "/"  #add the trailing / if needed

    headers = {}
    if bearerToken:
      headers["Authorization"] = "Bearer " + bearerToken

    rootProcessGroupsURL = baseURL + "nifi-api/flow/process-groups/root"
    resp = requests.get(url=rootProcessGroupsURL, headers=headers, verify=False)
    groupDict = dict(resp.json())

    # start with the root groups
    if groupDict["processGroupFlow"]:
      if groupDict["processGroupFlow"]["flow"]:
        if groupDict["processGroupFlow"]["flow"]["processGroups"]:
          if len(groupDict["processGroupFlow"]["flow"]["processGroups"])>0:
            return "deployed"

    return "notDeployed"

if __name__ == '__main__':
    print(main())