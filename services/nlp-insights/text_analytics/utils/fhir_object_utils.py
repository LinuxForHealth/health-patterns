import base64
import json

from fhir.resources.attachment import Attachment
from fhir.resources.bundle import Bundle
from fhir.resources.bundle import BundleEntry
from fhir.resources.bundle import BundleEntryRequest
from fhir.resources.coding import Coding
from fhir.resources.extension import Extension
from fhir.resources.identifier import Identifier
from fhir.resources.meta import Meta
from fhir.resources.reference import Reference
from text_analytics.insights import insight_constants


def create_coding(system, code, display=None):
    coding_element = Coding.construct()
    coding_element.system = system
    coding_element.code = code
    if display is not None:
        coding_element.display = display
    return coding_element


def create_confidence(name, value):
    confidence = Extension.construct()
    confidence.url = insight_constants.INSIGHT_CONFIDENCE_URL
    confidence_name = Extension.construct()
    confidence_name.url = insight_constants.INSIGHT_CONFIDENCE_NAME_URL
    confidence_name.valueString = name
    confidence_score = Extension.construct()
    confidence_score.url = insight_constants.INSIGHT_CONFIDENCE_SCORE_URL
    confidence_score.valueString = value
    confidence.extension = [confidence_name]
    confidence.extension.append(confidence_score)
    return confidence


# Adds insight reference extension for use within the actual resource
# This adds the classification and insight id to an extension that can be
# attached to a field like MedicationStatement.dosage or CodeableConcept.coding
def create_insight_reference(insight_id, insight_system):
    object_ext = Extension.construct()
    object_ext.url = insight_constants.INSIGHT_REFERENCE_URL

    classification_ext = Extension.construct()
    classification_ext.url = insight_constants.INSIGHT_CLASSIFICATION_URL
    classification_value = Coding.construct()
    classification_value.system = insight_constants.INSIGHT_CLASSIFICATION_SYSTEM
    classification_value.code = insight_constants.CLASSIFICATION_DERIVED
    classification_ext.valueCoding = classification_value

    insight_id_ext = Extension.construct()
    insight_id_ext.url = insight_constants.INSIGHT_RESULT_ID_URL
    insight_identifier = Identifier.construct()
    insight_identifier.system = insight_system
    insight_identifier.value = insight_id
    insight_id_ext.valueIdentifier = insight_identifier

    object_ext.extension = [classification_ext]
    object_ext.extension.append(insight_id_ext)

    return object_ext


# Creating coding system entry with the extensions for classfication/insight id
def create_coding_system_entry(coding_system_url, code_id, insight_id, insight_system):
    coding = create_coding(coding_system_url, code_id)
    coding.extension = [create_insight_reference(insight_id, insight_system)]
    return coding


# Adds extension with insight id
# Only used when another insight already exists and has already
# created the extension with the classification, ie "derived"
def add_insight_id(object_extension, insight_id, insight_system):
    insight_id_ext = Extension.construct()
    insight_id_ext.url = insight_constants.INSIGHT_RESULT_ID_URL
    insight_identifier = Identifier.construct()
    insight_identifier.system = insight_system
    insight_identifier.value = insight_id
    insight_id_ext.valueIdentifier = insight_identifier
    object_extension.append(insight_id_ext)


# fhir_resource_action --> list of resource(s) with their request type ('POST' or 'PUT') and url
#                    example: [[resource1, 'POST', 'url1'], [resource2, 'PUT', 'url2']]
def create_transaction_bundle(fhir_resource_action):
    bundle = Bundle.construct()
    bundle.type = "transaction"
    bundle.entry = []

    for resource, request_type, url in fhir_resource_action:
        bundle_entry = BundleEntry.construct()
        bundle_entry.resource = resource
        json = {
            "method": request_type,
            "url": url
        }
        request = BundleEntryRequest.parse_obj(json)
        bundle_entry.request = request
        bundle.entry.append(bundle_entry)

    return bundle


# Adds process meta extensions common across all insights,
# Does not check if these extensions already exist.
def _add_resource_meta(meta):
    result_extension = Extension.construct()
    result_extension.url = insight_constants.INSIGHT_RESULT_URL

    process_name_extension = Extension.construct()
    process_name_extension.url = insight_constants.PROCESS_NAME_URL
    process_name_extension.valueString = insight_constants.PROCESS_NAME
    result_extension.extension = [process_name_extension]

    process_version_extension = Extension.construct()
    process_version_extension.url = insight_constants.PROCESS_VERSION_URL
    process_version_extension.valueString = insight_constants.PROCESS_VERSION
    result_extension.extension.append(process_version_extension)

    meta.extension = [result_extension]


def add_resource_meta_unstructured(nlp, diagnostic_report):
    meta = Meta.construct()
    _add_resource_meta(meta)
    result_extension = meta.extension[0]

    process_type_extension = Extension.construct()
    process_type_extension.url = insight_constants.PROCESS_TYPE_URL
    process_type_extension.valueString = nlp.PROCESS_TYPE_UNSTRUCTURED
    result_extension.extension.append(process_type_extension)

    based_on_extension = Extension.construct()
    based_on_extension.url = insight_constants.INSIGHT_BASED_ON_URL
    reference = Reference.construct()
    reference.reference = diagnostic_report.resource_type + "/" + diagnostic_report.id
    based_on_extension.valueReference = reference
    result_extension.extension.append(based_on_extension)

    return meta


# Creates resource "meta:" section if it does not exist.
# Adds the extensions in the meta for the resource, if an extension does not already exist.
# This method currently does NOT check if the extension matches our insights.
def add_resource_meta_structured(nlp, resource):
    # Create meta if it doesn't exist
    if resource.meta is None:
        new_meta = Meta.construct()
        resource.meta = new_meta
    meta = resource.meta

    # Assuming any extension is ours at this time.  May need to do further check to verify.
    if resource.meta.extension is not None:
        return

    # Add process meta common across all insights
    _add_resource_meta(meta)
    result_extension = meta.extension[0]

    # Add structured process meta extension
    process_type_extension = Extension.construct()
    process_type_extension.url = insight_constants.PROCESS_TYPE_URL
    process_type_extension.valueString = nlp.PROCESS_TYPE_STRUCTURED
    result_extension.extension.append(process_type_extension)


def create_derived_resource_extension(resource):
    # add extension indicating resource was derived (created from insights)
    resource_ext = Extension.construct()
    resource_ext.url = insight_constants.INSIGHT_REFERENCE_URL
    resource_ext_nested = Extension.construct()
    resource_ext.extension = [resource_ext_nested]
    resource_ext_nested.url = insight_constants.INSIGHT_CLASSIFICATION_URL
    classification = Coding.construct()
    classification.system = insight_constants.INSIGHT_CLASSIFICATION_URL
    classification.code = insight_constants.CLASSIFICATION_DERIVED
    resource_ext_nested.valueCoding = classification
    resource.extension = [resource_ext]


def create_insight_span_extension(concept):
    offset_begin = Extension.construct()
    offset_begin.url = insight_constants.INSIGHT_SPAN_OFFSET_BEGIN_URL
    offset_begin.valueInteger = concept.get('begin')
    offset_end = Extension.construct()
    offset_end.url = insight_constants.INSIGHT_SPAN_OFFSET_END_URL
    offset_end.valueInteger = concept.get('end')
    covered_text = Extension.construct()
    covered_text.url = insight_constants.INSIGHT_SPAN_COVERED_TEXT_URL
    covered_text.valueString = concept.get('coveredText')

    insight_span = Extension.construct()
    insight_span.url = insight_constants.INSIGHT_SPAN_URL
    insight_span.extension = [covered_text]
    insight_span.extension.append(offset_begin)
    insight_span.extension.append(offset_end)

    return insight_span


def create_insight_extension(insight_id_string, insight_system):
    insight_id_ext = Extension.construct()
    insight_id_ext.url = insight_constants.INSIGHT_INSIGHT_ID_URL
    insight_id = Identifier.construct()
    insight_id.system = insight_system
    insight_id.value = insight_id_string
    insight_id_ext.valueIdentifier = insight_id
    return insight_id_ext


def create_insight_detail_extension(nlp_output):
    nlp_dict = nlp_output #.to_dict()
    nlp_dict_string = json.dumps(nlp_dict)  # get the string
    nlp_as_bytes = nlp_dict_string.encode('utf-8')  # convert to bytes including utf8 content
    nlp_base64_encoded_bytes = base64.b64encode(nlp_as_bytes)  # encode to base64
    nlp_base64_ascii_string = nlp_base64_encoded_bytes.decode("ascii")  # convert base64 bytes to ascii characters
    insight_detail = Extension.construct()
    insight_detail.url = insight_constants.INSIGHT_EVIDENCE_DETAIL_URL
    attachment = Attachment.construct()
    attachment.contentType = "json"
    attachment.data = nlp_base64_ascii_string  # data is an ascii string of encoded data
    insight_detail.valueAttachment = attachment
    return insight_detail


# ACD will often return multiple codes from one system in a comma delimited list
# Split the list, then create a separate coding system entry for each one
def create_coding_entries(codeable_concept, code_url, code_ids, insight_id, insight_system):
    ids = code_ids.split(",")
    for id in ids:
        code_entry = find_codable_concept(codeable_concept, id, code_url)
        if code_entry is not None and code_entry.extension is not None and code_entry.extension[
            0].url == insight_constants.INSIGHT_REFERENCE_URL:
            # there is already a derived extension
            add_insight_id(code_entry.extension[0].extension, insight_id, insight_system)
        else:
            # the Concept exists, but no derived extension
            coding = create_coding_system_entry(code_url, id, insight_id, insight_system)
            codeable_concept.coding.append(coding)


def add_codings(concept, codeable_concept, insight_id, insight_system):
    if 'cui' in concept:
        # For CUIs, we do not handle comma-delimited values (have not seen that we ever have more than one value)
        # We use the preferred name from UMLS for the display text
        code_entry = find_codable_concept(codeable_concept, concept['cui'], insight_constants.UMLS_URL)
        if code_entry is not None and code_entry.extension is not None and code_entry.extension[
            0].url == insight_constants.INSIGHT_REFERENCE_URL:
            # there is already a derived extension
            add_insight_id(code_entry.extension[0].extension, insight_id, insight_system)
        else:
            # the Concept exists, but no derived extension
            coding = create_coding_system_entry(insight_constants.UMLS_URL, concept['cui'], insight_id, insight_system)
            coding.display = concept["preferredName"]
            codeable_concept.coding.append(coding)
    if "snomedConceptId" in concept:
        create_coding_entries(codeable_concept, insight_constants.SNOMED_URL, concept["snomedConceptId"], insight_id,
                              insight_system)
    if "nciCode" in concept:
        create_coding_entries(codeable_concept, insight_constants.NCI_URL, concept["nciCode"], insight_id,
                              insight_system)
    if "loincId" in concept:
        create_coding_entries(codeable_concept, insight_constants.LOINC_URL, concept["loincId"], insight_id,
                              insight_system)
    if "meshId" in concept:
        create_coding_entries(codeable_concept, insight_constants.MESH_URL, concept["meshId"], insight_id,
                              insight_system)
    if "icd9Code" in concept:
        create_coding_entries(codeable_concept, insight_constants.ICD9_URL, concept["icd9Code"], insight_id,
                              insight_system)
    if "icd10Code" in concept:
        create_coding_entries(codeable_concept, insight_constants.ICD10_URL, concept["icd10Code"], insight_id,
                              insight_system)
    if "rxNormId" in concept:
        create_coding_entries(codeable_concept, insight_constants.RXNORM_URL, concept["rxNormId"], insight_id,
                              insight_system)


def add_codings_drug(drug, drug_name, codeable_concept, insight_id, insight_system):
    if drug.get("cui") is not None:
        # For CUIs, we do not handle comma-delimited values (have not seen that we ever have more than one value)
        # We use the preferred name from UMLS for the display text
        code_entry = find_codable_concept(codeable_concept, drug.get("cui"), insight_constants.UMLS_URL)
        if code_entry is not None and code_entry.extension is not None and code_entry.extension[
            0].url == insight_constants.INSIGHT_REFERENCE_URL:
            # there is already a derived extension
            add_insight_id(code_entry.extension[0].extension, insight_id, insight_system)
        else:
            # the Concept exists, but no derived extension
            coding = create_coding_system_entry(insight_constants.UMLS_URL, drug.get("cui"), insight_id,
                                                insight_system)

            coding.display = drug_name
            
            codeable_concept.coding.append(coding)
    if drug.get("rxNormID") is not None:
        create_coding_entries(codeable_concept, insight_constants.RXNORM_URL, drug.get("rxNormID"), insight_id,
                              insight_system)


'''
Looks through the array of the codeable_concept for an entry matching the id and system.
Returns the entry if found, or None if not found.
'''


def find_codable_concept(codeable_concept, id, system):
    for entry in codeable_concept.coding:
        if entry.system == system and entry.code == id:
            return entry
    return None


def add_diagnosis_confidences(insight_ext, insight_model_data):
    if insight_model_data['diagnosis'] is not None:
        if insight_model_data['diagnosis']['usage'] is not None:
            if insight_model_data['diagnosis']['usage']['explicitScore'] is not None:
                confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_EXPLICIT,
                                               insight_model_data['diagnosis']['usage']['explicitScore'])
                insight_ext.append(confidence)
            if insight_model_data['diagnosis']['usage']['patientReportedScore'] is not None:
                confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_PATIENT_REPORTED,
                                               insight_model_data['diagnosis']['usage']['patientReportedScore'])
                insight_ext.append(confidence)
            if insight_model_data['diagnosis']['usage']['discussedScore'] is not None:
                confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_DISCUSSED,
                                               insight_model_data['diagnosis']['usage']['discussedScore'])
                insight_ext.append(confidence)
            if insight_model_data['diagnosis']['usage']['familyHistoryScore'] is not None:
                confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_FAMILY_HISTORY,
                                               insight_model_data['diagnosis']['familyHistoryScore'])
                insight_ext.append(confidence)
            if insight_model_data['diagnosis']['usage']['suspectedScore'] is not None:
                confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_SUSPECTED,
                                               insight_model_data['diagnosis']['suspectedScore'])
                insight_ext.append(confidence)


def add_medication_confidences(insight_ext, insight_model_data):
    # Medication has 5 types of confidence scores
    # For alpha only pulling medication.usage scores
    # Not using startedEvent scores, stoppedEvent scores, doseChangedEvent scores, adversetEvent scores
    confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_MEDICATION_TAKEN,
                                   insight_model_data['medication']['usage']['takenScore'])
    insight_ext.append(confidence)

    confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_MEDICATION_CONSIDERING,
                                   insight_model_data['medication']['usage']['consideringScore'])
    insight_ext.append(confidence)
    confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_MEDICATION_DISCUSSED,
                                   insight_model_data['medication']['usage']['discussedScore'])
    insight_ext.append(confidence)
    confidence = create_confidence(insight_constants.CONFIDENCE_SCORE_MEDICATION_MEASUREMENT,
                                   insight_model_data['medication']['usage']['labMeasurementScore'])
    insight_ext.append(confidence)


'''
Returns the attached document as a string, decoded.
Parameters:
  diagnostic_report - fhir.resources.diagnosticreport object where the text will be retrieved
'''


def get_diagnostic_report_data(diagnostic_report):
    if diagnostic_report.presentedForm:
        encoded_data = diagnostic_report.presentedForm[0].data
        byte_text = base64.b64decode(encoded_data)
        text = byte_text.decode('utf8')  # This removes the b'..' around the text string
        return text
    
    return None
