"""
Defines an NLP service concrete class for QuickUMLS NLP.

"""
import json
import logging
from typing import Dict, Any
from typing import List
from typing import NamedTuple

from fhir.resources.resource import Resource
import requests

from nlp_insights.fhir.create_bundle import BundleEntryDfn
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.abstract_nlp_service import NLPService, NLPServiceError
from nlp_insights.nlp.nlp_config import QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.nlp_response import NlpResponse, NlpCui
from nlp_insights.nlp.quickUMLS.fhir_enrichment.insights.create_condition import (
    create_conditions_from_insights,
)
from nlp_insights.nlp.quickUMLS.fhir_enrichment.insights.create_medication import (
    create_med_statements_from_insights,
)
from nlp_insights.nlp.quickUMLS.fhir_enrichment.insights.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    NlpConceptRef,
)
from nlp_insights.umls.semtype_lookup import get_names_from_type_ids


logger = logging.getLogger(__name__)


class _ResultEntry(NamedTuple):
    """Tracks nlp input and output"""

    text_source: UnstructuredText
    nlp_output: NlpResponse


def create_nlp_response(server_response_concepts: List[Dict[str, Any]]) -> NlpResponse:
    """Converts a json response from the quickUmls server to an NlpResponse

    The server's response is a list of concept objects, each of which must
    have a UMLS cui and optionally other fields as well.
    """
    nlp_cuis = [
        NlpCui(
            cui=concept["cui"],
            covered_text=concept["ngram"] if "ngram" in concept else "",
            begin=concept["start"] if "start" in concept else 0,
            end=concept["end"] if "end" in concept else 0,
            preferred_name=concept["term"] if "term" in concept else "",
            types=(
                get_names_from_type_ids(concept["semtypes"])
                if "semtypes" in concept
                else set()
            ),
            snomed_ct=concept["snomed_ct"] if "snomed_ct" in concept else None,
        )
        for concept in server_response_concepts
        if "cui" in concept
    ]
    return NlpResponse(nlp_cuis=nlp_cuis)


class QuickUMLSService(NLPService):
    """
    The QuickUMLS Service is able to detect UMLS cuis in unstructured text.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.quick_umls_url = config["config"]["endpoint"]
        self.nlp_config = QUICK_UMLS_NLP_CONFIG

    def _run_nlp(self, text: str) -> NlpResponse:
        logger.info("Calling QUICKUMLS-%s with text %s", self.config_name, text)

        request_body = {"text": text}
        try:
            resp = requests.post(self.quick_umls_url, json=request_body)
        except requests.exceptions.RequestException as ex:
            raise NLPServiceError(
                description=f"NLP using config {self.config_name} "
                f"failed with an error {type(ex).__name__}"
            ) from ex
        if not resp.ok:
            raise NLPServiceError(
                description=f"NLP using config {self.config_name} "
                f"failed with an error {resp.status_code} {resp.reason}"
            )
        concepts = json.loads(resp.text)
        return create_nlp_response(concepts)

    def derive_new_resources(
        self, notes: List[UnstructuredText]
    ) -> List[BundleEntryDfn]:

        nlp_responses = [_ResultEntry(note, self._run_nlp(note.text)) for note in notes]

        new_resources: List[Resource] = []
        for response in nlp_responses:
            conditions = create_conditions_from_insights(
                response.text_source, response.nlp_output, self.nlp_config
            )
            if conditions:
                new_resources.extend(conditions)

            medications = create_med_statements_from_insights(
                response.text_source, response.nlp_output, self.nlp_config
            )

            if medications:
                new_resources.extend(medications)

        return [
            BundleEntryDfn(resource=resource, method="POST", url=resource.resource_type)
            for resource in new_resources
        ]

    def enrich_codeable_concepts(
        self, resource: Resource, concept_refs: List[AdjustedConceptRef]
    ) -> int:

        nlp_responses = [
            NlpConceptRef(concept_ref, self._run_nlp(concept_ref.adjusted_text))
            for concept_ref in concept_refs
        ]

        return update_codeable_concepts_and_meta_with_insights(
            resource, nlp_responses, self.nlp_config
        )
