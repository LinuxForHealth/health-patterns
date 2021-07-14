from flask import Flask, request
from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService
import json
from enhance.enhance_allergy_intolerance_payload import enhance_allergy_intolerance_payload_to_fhir
from enhance.enhance_diagnostic_report_payload import enhance_diagnostic_report_payload_to_fhir
from enhance.enhance_immunization_payload import enhance_immunization_payload_to_fhir

app = Flask(__name__)

nlp_service = None


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/configure/", methods=['POST'])
def setup_nlp():
    global nlp_service
    configJson = json.loads(request.data)
    if configJson["nlpService"] == "ACD":
        nlp_service = ACDService(request.data)
        return request.data
    if configJson["nlpService"] == "quickUMLS":
        nlp_service = QuickUMLSService(request.data)
        return request.data

@app.route("/process/", methods=['POST'])
def apply_analytics():
    request_data = request.data
    if nlp_service is not None:
        # resp = nlp_service.process(request_data)
        resp = nlp_service.process(request_data)
        return str(resp)
    return "Internal Server Error"


@app.route("/processAllergy", methods=['POST'])
def process_Allergy():
    request_data = json.loads(request.data)
    if nlp_service is not None:
        resp = enhance_allergy_intolerance_payload_to_fhir(nlp_service, request_data)
        return resp.json()
    return "NLP service not specified"


@app.route("/processDiagnosticReport", methods=['POST'])
def process_Diagnostic_Report():
    request_data = json.loads(request.data)
    if nlp_service is not None:
        resp = enhance_diagnostic_report_payload_to_fhir(nlp_service, request_data)
        return str(resp)
    return "NLP service not specified"


@app.route("/processImmunization", methods=['POST'])
def process_Immunization():
    request_data = json.loads(request.data)
    if nlp_service is not None:
        resp = enhance_immunization_payload_to_fhir(nlp_service, request_data)
        return str(resp)
    return "NLP service not specified"
