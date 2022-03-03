import requests

import os
import json
import copy
import time

from urllib.request import urlopen

from flask import Flask, request
from flask import jsonify

import ibm_boto3
from ibm_botocore.client import Config

from datetime import datetime

from concurrent.futures import ThreadPoolExecutor

import uuid

status_dict = {}

cohort_endpoint = os.getenv("COHORT_ENDPOINT")
fhir_endpoint = os.getenv("FHIR_ENDPOINT")
fhiruser = os.getenv("FHIRUSER")
fhirpw = os.getenv("FHIRPW")
cos_endpoint = os.getenv("COS_ENDPOINT")
cos_api_key = os.getenv("COS_API_KEY")
cos_instance_crn = os.getenv("COS_INSTANCE_CRN")
bucket_name = os.getenv("BUCKET_NAME")
resource_list_raw = os.getenv("RESOURCE_LIST")

app = Flask(__name__)

def generate_response(statuscode, otherdata={}):
    message = {
        "status": str(statuscode)
    }

    message.update(otherdata)
    resp = jsonify(message)
    resp.status_code = statuscode
    return resp

def cql_bulk_processing(cql, job_id):
    def get_patient_ids(cohort_endpoint, cql_name):
        # call of to cohort service to get patient ids for this cohort

        baseurl = cohort_endpoint + "/libraries/" + cql_name + "/patientIds"
        resp = requests.get(baseurl, verify=False)
        return list(resp.json())

    def create_group_definition(patient_ids):
        # create a FHIR resource Group for these patients
        f = open("grouptemplate.json", "r")
        json_skeleton = json.loads(f.read())
        member_list = json_skeleton["entry"][0]["resource"]["member"]

        fragment = {
            "entity": {
                "reference": "Patient/id"
            },
            "period": {
                "start": "2000-01-01"
            }
        }

        for id in patient_ids:
            refid = "Patient/" + id
            fragment_copy = copy.deepcopy(fragment)
            fragment_copy["entity"]["reference"] = refid
            member_list.append(fragment_copy)

        result = json.dumps(json_skeleton)

        return result

    def post_group_to_fhir(group_json):
        # post the Group resource to FHIR server

        headers = {'Content-Type': 'application/fhir+json'}
        response = requests.post(fhir_endpoint,
                                 auth=(fhiruser, fhirpw),
                                 verify=False,
                                 data=group_json,
                                 headers=headers)

        resp = response.json()
        group_id = resp["entry"][0]["response"]["id"]
        return group_id

    def group_bulk_export(group_id):
        # perform a bulk export for the group of patients previously identified
        # possibly limited by the resource list if it exists

        bulk_group_endpoint = fhir_endpoint + "/Group/" + group_id + "/$export?_outputFormat=application/fhir+ndjson"
        if len(resource_list_raw) > 0:
            bulk_group_endpoint = bulk_group_endpoint + "&_type=" + resource_list_raw

        headers = {}
        response = requests.get(bulk_group_endpoint,
                                auth=(fhiruser, fhirpw),
                                verify=False,
                                headers=headers)

        url_dict = {}

        respStatusCode = response.status_code
        if respStatusCode != 202:
            raise Exception("ERROR in bulk export...return error message")
        else:
            # export in progress since response code is 202
            # get and check status-need url

            info = dict(response.headers)
            jobstatusURL = info["Content-Location"]  # need to call this until 200 (or error)
            parts = jobstatusURL.split("fhir-server/api/v4") # need to use internal fhir url
            jobstatusURL = fhir_endpoint + parts[1]

            statusresp = requests.get(jobstatusURL, auth=(fhiruser, fhirpw), verify=False)
            respStatusCode = statusresp.status_code
            while respStatusCode == 202:
                time.sleep(2)  # wait for a bit to see if export completes
                statusresp = requests.get(jobstatusURL, auth=(fhiruser, fhirpw), verify=False)
                respStatusCode = statusresp.status_code

            if respStatusCode == 200:
                # export is done, get the object name from status response, else other code means error
                status_result = statusresp.json()
                for item in status_result["output"]:
                    url_dict[item["type"]] = item["url"]
                return url_dict
            else:
                raise Exception(
                    "ERROR-bulk export did not complete properly-returned status code " + str(respStatusCode))

    def build_new_temp_ndjson_file(cos_urls, id):
        lines = 0
        local_file_name = "temp-" + id + ".ndjson"
        out_file = open(local_file_name, "w")

        cos_delete_client = ibm_boto3.client("s3",
                                             ibm_api_key_id=cos_api_key,
                                             ibm_service_instance_id=cos_instance_crn,
                                             config=Config(signature_version="oauth"),
                                             endpoint_url=cos_endpoint
                                             )

        resources = cos_urls.keys()
        resources = sorted(resources)
        for resource in resources:
            resource_url = cos_urls[resource]
            parts = resource_url.split("/")
            del_key = parts[-2] + "/" + (parts[-1].split("ndjson")[0]) + "ndjson"

            if "Group" not in resource:  # skip processing group resources
                f = urlopen(resource_url)
                for aline in f:
                    lines = lines + 1
                    out_file.write((aline.decode("utf-8")))

            result = cos_delete_client.delete_object(Bucket=bucket_name, Key=del_key)
            print(result)

        out_file.close()
        return {"file_name": local_file_name,
                "resource_count": lines}

    def push_file_to_cos(source_file, target_name):

        cos_client = ibm_boto3.client("s3",
                                      ibm_api_key_id=cos_api_key,
                                      ibm_service_instance_id=cos_instance_crn,
                                      config=Config(signature_version="oauth"),
                                      endpoint_url=cos_endpoint
                                      )

        cos_client.upload_file(Filename=source_file, Bucket=bucket_name, Key=target_name)


    # library request parm exists so try to process
    # take a cql and run it against the current contents of the fhir server
    #
    # first, check that the cql is valid
    baseurl = cohort_endpoint + "/libraries"
    resp = requests.get(baseurl, verify=False)
    if resp.status_code == 200:
        lib_list = []
        for item in resp.json():
            if "FHIRHelpers" not in item["name"]:
                lib_id = item["id"]
                lib_list.append(lib_id)
        if cql not in lib_list:
            other = {"available libraries": str(lib_list),
                                           "message": cql + " not in available list"}
            status_dict[job_id] = {"status": "done", "info": other}
    else:
        other = {"message": "Cohort libraries not available"}
        status_dict[job_id] = {"status":"done", "info":other}


    #cql is in the list so go ahead and generate cohort data

    try:

        patient_ids = get_patient_ids(cohort_endpoint, cql)

        # get back a list of ids

        # for each id...
        #      add them to a groupdef json structure

        group_json = create_group_definition(patient_ids)

        # post the group definition (response has the group ID)
        group_id = post_group_to_fhir(group_json)

        # perform bulk export using group (get all resources)
        #    returns a list of cos buckets

        cos_urls = group_bulk_export(group_id)

        # for each cos bucket...
        #    read the cos bucket and add the ndjson entries (lines) to a final result ndjson file
        local_file_name_dict = build_new_temp_ndjson_file(cos_urls, job_id)
        local_file_name = local_file_name_dict["file_name"]
        total_resources = local_file_name_dict["resource_count"]
        # UPLOAD the file to a cos bucket
        parts = cql.split("-")
        cql_name = parts[0]
        target_name = cql_name + ".ndjson"
        push_file_to_cos(local_file_name, target_name)
        os.remove(local_file_name)

        other = {"cos_target": target_name,
                                       "cos_bucket": bucket_name,
                                       "number_of_resources": total_resources,
                                       "number_of_patients": len(patient_ids)}
        status_dict[job_id] = {"status":"done", "info":other}

    except Exception as e:
        status_dict[job_id] = {"status": "error",
                               "info": {
                                  "message": "Something went wrong in the cql bulk export processing",
                                  "exception text": str(e)}
                               }


@app.route("/", methods=['GET'])
def cql_bulkextract(cql = None):

    cql = ""
    if 'cql' in request.args:
        cql = request.args.get("cql")

    if len(cql) == 0:
        # no cql libary... 500 error
        return generate_response(500, {"message": "CQL Libary not found: must include a cql library name to bulk export (GET)"})

    ex = ThreadPoolExecutor(max_workers=2)
    target_name = cql.split("-")[0] + ".ndjson"
    job_id = str(uuid.uuid4())
    message = "Started process to build " + target_name + " JOB ID=" + job_id
    status_data = {"status": "working",
                   "info" : {"job id": job_id,
                             "target name": target_name}}
    status_dict[job_id] = status_data
    ex.submit(cql_bulk_processing, cql, job_id)

    return generate_response(202, {"message": message})


@app.route("/healthcheck", methods=['GET'])
def healthcheck():

    now = datetime.now()
    current_time_date = now.strftime("%Y-%m-%d %H:%M:%S")
    return generate_response(200, {"message": "CQL bulkexport service is running..." + current_time_date + "GMT"})

@app.route("/cql_libraries", methods=["GET"])
def get_cql_library():
    baseurl = cohort_endpoint + "/libraries"
    resp = requests.get(baseurl, verify=False)
    if resp.status_code == 200:
        lib_list = []
        for item in resp.json():
            if "FHIRHelpers" not in item["name"]:
                lib_id = item["id"]
                lib_list.append(lib_id)

        return generate_response(200, {"available cql libraries": str(lib_list)})
    else:
        generate_response(500, {"message": "Cohort libraries not available"})

@app.route("/status", methods=['GET'])
def get_status():

    id = ""
    if 'id' in request.args:
        id = request.args.get("id")

    if len(id) == 0:
        return generate_response(500, {"message": "Must include job id"})

    if id not in status_dict:
        return generate_response(500, {"message": "Job id does not exist"})

    status = status_dict[id]
    if status["status"] == 'working':
        r_code = 202
    elif status["status"] == 'done':
        r_code = 200
    elif status["status"] == 'error':
        r_code = 500
    else:
        r_code = 500

    return generate_response(r_code, status)

if __name__ == '__main__':
   app.run(threaded=True)
