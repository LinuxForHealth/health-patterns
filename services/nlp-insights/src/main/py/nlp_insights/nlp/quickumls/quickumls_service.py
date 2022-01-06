"""
Defines an NLP service concrete class for QuickUMLS NLP.

"""
import json
import logging
from typing import Dict, Any
from typing import List

from fhir.resources.resource import Resource
import requests

from nlp_insights.fhir.create_bundle import BundleEntryDfn
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.abstract_nlp_service import NLPService, NLPServiceError
from nlp_insights.nlp.nlp_config import QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.quickumls.concept_container import (
    QuickUmlsConcept,
    QuickUmlsConceptContainer,
)
from nlp_insights.nlp.quickumls.quickumls_to_fhir.fhir_resource.create.create_condition import (
    ConditionBuilder,
)
from nlp_insights.nlp.quickumls.quickumls_to_fhir.fhir_resource.create.create_medication import (
    MedicationStatementBuilder,
)
from nlp_insights.nlp.quickumls.quickumls_to_fhir.fhir_resource.update.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    QuickumlsConceptRef,
)
from nlp_insights.umls.semtype_lookup import get_names_from_type_ids


logger = logging.getLogger(__name__)


def create_nlp_response(
    server_response_concepts: List[Dict[str, Any]], response: str
) -> QuickUmlsConceptContainer:
    """Converts a json response from the quickUmls server to an object

    The server's response is a list of concept objects, each of which must
    have a UMLS cui and optionally other fields as well.
    """
    concepts = [
        QuickUmlsConcept(
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
            similarity=concept.get("similarity", 0.0),
        )
        for concept in server_response_concepts
        if "cui" in concept
    ]
    return QuickUmlsConceptContainer(concepts=concepts, service_resp=response)


class QuickUmlsService(NLPService):
    """
    The QuickUMLS Service is able to detect UMLS cuis in unstructured text.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.quick_umls_url = config["config"]["endpoint"]
        self.nlp_config = QUICK_UMLS_NLP_CONFIG

    def _run_nlp(self, text: str) -> QuickUmlsConceptContainer:
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
        return create_nlp_response(concepts, resp.text)

    def derive_new_resources(
        self, notes: List[UnstructuredText]
    ) -> List[BundleEntryDfn]:

        new_resources: List[Resource] = []

        for note in notes:
            container = self._run_nlp(note.text)

            new_resources.extend(
                ConditionBuilder(
                    note,
                    container,
                    self.nlp_config,
                ).build_resources()
            )

            new_resources.extend(
                MedicationStatementBuilder(
                    note,
                    container,
                    self.nlp_config,
                ).build_resources()
            )

        return [
            BundleEntryDfn(resource=resource, method="POST", url=resource.resource_type)
            for resource in new_resources
        ]

    def enrich_codeable_concepts(
        self, resource: Resource, concept_refs: List[AdjustedConceptRef]
    ) -> int:

        nlp_responses = [
            QuickumlsConceptRef(concept_ref, self._run_nlp(concept_ref.adjusted_text))
            for concept_ref in concept_refs
        ]

        return update_codeable_concepts_and_meta_with_insights(
            nlp_responses, self.nlp_config
        )
