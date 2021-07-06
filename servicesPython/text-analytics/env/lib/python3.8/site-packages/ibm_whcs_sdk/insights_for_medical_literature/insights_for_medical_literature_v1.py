# coding: utf-8

# (C) Copyright IBM Corp. 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
For more information see the <a href='../../documentation' target='_blank'>extended
documentation</a>.<p>Try the <a href='../../application'>Insights for Medical Literature
demo application</a>.<h3>Service Overview</h3>The Insights for Medical Literature service
provides APIs that enable you to derive insights from a corpus of medical documents. For
example, the <a href='https://www.nlm.nih.gov/bsd/pmresources.html'
target='_blank'>MEDLINE&reg;</a> corpus contains more than 26 million references to
medical journal articles.  An unstructured medical document corpus is ingested by IBM,
enriched with the Unified Medical Language System (<a
href='https://www.nlm.nih.gov/research/umls/'  target='_blank'>UMLS&reg;</a>) and stored
as structured data in an IBM managed database.  The UMLS enrichment enables a concept
based search, in addition to a conventional text search.  Other unique features include
concept matching, concept relationships, identifying co-occurring concepts and identifying
disorders, drugs, genes and other medical terms mentioned in a medical
document.<h3>National Library of Medicine&reg; (NLM&reg;) License</h3>The MEDLINE corpus
is imported from <a href='https://www.nlm.nih.gov/databases/journal.html'
target='_blank'>MEDLINE&reg;/PubMed&reg;</a>, a database of the U.S. National Library of
Medicine. <P><P>The MEDLINE corpus is periodically updated to contain new and/or
maintained records, and remove deleted records, at least once every thirty (30) days. The
MEDLINE corpus may be updated on a weekly basis.<P><P>NLM represents that its data were
formulated with a reasonable standard of care.  Except for this representation, NLM makes
no representation or warranties, expressed or implied.  This includes, but is not limited
to, any implied warranty of merchantability or fitness for a particular purpose, with
respect to the NLM data, and NLM specifically disclaims any such warranties and
representations.<P><P>All complete or parts of U.S. National Library of Medicine (NLM)
records that are redistributed or retransmitted must be identified as being derived from
NLM  data.<h3>API Overview</h3>The APIs are grouped into these
categories:<UL><LI><B>Concepts</B> : Concept information</LI><P>Concept information
includes a concept unique identifier (CUI), preferred name, alternative name (other
surface forms), semantic group (category), semantic types, counts (hits, parents,
children, siblings...) and, related concepts. <LI><B>Corpora</B> : Corpora
information</LI><P>You can retrieve a list of corpus names.  For each corpus a unique list
of semantic groups and semantic types is provided. <LI><B>Documents</B> : Document
information</LI><P>These APIs enable full text documents and document annotations to be
retreived.  Concepts mentioned in a medical document may also be categorized by semantic
groups and types.  The best matching search concepts can also be identified in a medical
document.<LI><B>Search</B> : Concept search</LI><P>These APIs perform typeahead concept
searches, ranked document searches, and cohesive and co-occurring concept searches.  A
search targets a single medical document corpus.<LI><B>Status</B> : Check the status of
this service</LI></UL><h3>Terminology</h3><UL><LI><B>Concept Unique Identifier
(cui)</B></LI>A UMLS CUI identifies a concept, and is specified as a path or query
parameter to select a specific concept.  A CUI always begins with an uppercase letter 'C'
followed by seven decimal digits (e.g., C0446516).<LI><B>Document Identifiter</B></LI>A
document ID uniquely identifies a document in a corpus, and is specified as a path or
query parameter to select a specific medical document.<LI><B>Hit count</B></LI>A hit count
specifies the number of times a specific concept is mentioned in a corpus.<LI><B>Preferred
Name (pn)</B></LI>A preferred name is the common name for a concept.  A concept may also
have other surface forms or alternative names.<LI><B>Semantic Group (group)</B></LI>A
semantic group aggregates multiple semantic types, and is specified as a path or query
parameter to filter or select concepts belonging to the same semantic group (e.g.,
Disorders or ChemicalsAndDrugs).<LI><B>Semantic Type (type)</B></LI>A semantic type is a
camelcase string derived from a UMLS semantic type (e.g., ClinicalDrug or
DiseaseOrSyndrome). It is specified as a path or query parameter to filter or select
concepts belonging to the same category (semantic type).<LI><B>Surface form</B></LI>A
surface form is an alternative name for a concept.  The surface forms identify text spans
in a medical document, and the identified text spans are annotated with the matching CUI,
preferred name and semantic type.</UL><h3>Typical Document Search Flow</h3><p>1. <b>GET
/v1/corpora</b> - Get list of all available corpus names<p>2. <b>GET
/v1/corpora/corpus_name/search/typeahead</b> - Use typeahead to select search
concepts<p>3. <b>GET /v1/corpora/corpus_name/search/cooccurring_concepts</b> - Find
additional co-occurring search concepts<p>4. <b>GET
/v1/corpora/corpus_name/concepts/{cui}/matching_concepts</b> - Find additional matching
search concepts<p>5. <b>GET /v1/corpora/corpus_name/concepts/{cui}/related_concepts</b> -
Find additional related search concepts<p>6. <b>GET
/v1/corpora/corpus_name/search/ranked_documents</b> - Search for ranked documents matching
search concepts<p>7. <b>GET
/v1/corpora/corpus_name/documents/{document_id}/search_matches</b> - Highlight matching
search concepts in a ranked documents<p>8. <b>GET
/v1/corpora/corpus_name/documents/{document_id}/categories</b> - Highlight diseases, drugs
and genes in a ranked document
"""

from enum import Enum
from typing import Dict, List
import json

from ibm_cloud_sdk_core import BaseService, DetailedResponse, ApiException
from ibm_cloud_sdk_core.authenticators.authenticator import Authenticator
from ibm_cloud_sdk_core.get_authenticator import get_authenticator_from_environment
from ibm_cloud_sdk_core.utils import convert_list, convert_model

from ibm_whcs_sdk.common import get_sdk_headers


##############################################################################
# Exception Handling
##############################################################################
class IMLException(Exception):
    """
    Custom exception class for errors returned from IML APIs.
    :param int code: The HTTP status code returned.
    :param str message: A message describing the error.
    :param str correlationId: A code to associate to the IML error
    """
    def __init__(self, code, message=None, correlation_id=None):
        # Call the base class constructor with the parameters it needs
        super(IMLException, self).__init__(message)
        self.message = message
        self.code = code
        self.correlation_id = correlation_id

    def __str__(self):
        msg = ('Error: ' + str(self.message) + ', Code: ' + str(self.code)
               + ' CorrelationId: ' + str(self.correlation_id))
        return msg

##############################################################################
# Service
##############################################################################

class InsightsForMedicalLiteratureServiceV1(BaseService):
    """The Insights for Medical Literature Service V1 service."""

    DEFAULT_SERVICE_URL = 'https://insights-for-medical-literature-service.cloud.ibm.com/services/medical_insights/api'
    DEFAULT_SERVICE_NAME = 'insights_for_medical_literature_service'

    @classmethod
    def new_instance(cls,
                     version: str,
                     service_name: str = DEFAULT_SERVICE_NAME,
                    ) -> 'InsightsForMedicalLiteratureServiceV1':
        """
        Return a new client for the Insights for Medical Literature Service service
               using the specified parameters and external configuration.

        :param str version: The release date of the version of the API you want to
               use. Specify dates in YYYY-MM-DD format.
        """
        if version is None:
            raise ValueError('version must be provided')

        authenticator = get_authenticator_from_environment(service_name)
        service = cls(
            version,
            authenticator
            )
        service.configure_service(service_name)
        return service

    def __init__(self,
                 version: str,
                 authenticator: Authenticator = None,
                ) -> None:
        """
        Construct a new client for the Insights for Medical Literature Service service.

        :param str version: The release date of the version of the API you want to
               use. Specify dates in YYYY-MM-DD format.

        :param Authenticator authenticator: The authenticator specifies the authentication mechanism.
               Get up to date information from https://github.com/IBM/python-sdk-core/blob/master/README.md
               about initializing the authenticator of your choice.
        """
        if version is None:
            raise ValueError('version must be provided')

        BaseService.__init__(self,
                             service_url=self.DEFAULT_SERVICE_URL,
                             authenticator=authenticator)
        self.version = version


    def request_iml(self, request=None):
        """
        Handle the request to IML.
        """

        try:
            response = self.send(request)
            if 200 <= response.status_code <= 299:
                return response
        except ApiException as api_except:
            final = api_except._get_error_message
            if api_except.message is not None:
                error_message = api_except.message
            else:
                error_message = "No error message available"
            if api_except.code is not None:
                status_code = api_except.code
            if (
                api_except.http_response is not None
                and api_except.http_response.headers is not None
                and api_except.http_response.headers.get('x-correlation-id') is not None
                ):
                correlation_id = api_except.http_response.headers.get('x-correlation-id')
            else:
                correlation_id = "None"
            raise IMLException(status_code, error_message, correlation_id)

        return final

    #########################
    # Documents
    #########################


    def get_documents(self, corpus: str, **kwargs) -> DetailedResponse:
        """
        Retrieves information about the documents in this corpus.

        The response returns the following information: <ul><li>number of documents in the
        corpus</li><li>corpus provider</li></ul>.

        :param str corpus: Corpus name.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorpusModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_documents')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def add_corpus_document(self, corpus: str, *, document: dict = None, acd_url: str = None, api_key: str = None, flow_id: str = None, access_token: str = None, other_annotators: List[object] = None, **kwargs) -> DetailedResponse:
        """
        Define enrichment document.

        The response returns whether the document was properly added to the corpus.
        <P>This API should be used for adding a document to a custom corpus.<P>Example
        POST body:<pre>{
          "acdUrl" :
          "acdApiKeyl" :
          "flowId" :
          "document" : {
           "doc_id" :
           "field[n]" : "value"
          }
          "otherAnnotators" : [   "{    "annotatorUrl    "annotatorApiKey
        "containerName   "}  ]
        }
        </pre>.

        :param str corpus: Corpus name.
        :param dict document: (optional) JSON based document for enrichment.
        :param str acd_url: (optional) Annotator for clincial data url.
        :param str api_key: (optional) Security key.
        :param str flow_id: (optional) Enrichment flow identifier.
        :param str access_token: (optional) Cloud access token.
        :param List[object] other_annotators: (optional) URLs and API keys for
               custom annotators.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='add_corpus_document')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'document': document,
            'acdUrl': acd_url,
            'apiKey': api_key,
            'flowId': flow_id,
            'accessToken': access_token,
            'otherAnnotators': other_annotators
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_iml(request)
        return response


    def get_document_info(self, corpus: str, document_id: str, *, verbose: bool = None, **kwargs) -> DetailedResponse:
        """
        Retrieves the external ID, title, abstract and text for a document.

        The response may return the following fields:<ul><li>external ID (e.g., PubMed
        ID)</li><li>title</li><li>abstract</li><li>body</li><li>pdfUrl</li><li>referenceUrl</li><li>other
        metadata</li></ul>Note, some documents may not have an abstract, or only the
        abstract may be available without the body text.

        :param str corpus: Corpus name.
        :param str document_id: Document ID.
        :param bool verbose: (optional) Verbose output. If true, text for all
               document sections is returned.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `GetDocumentInfoResponse` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if document_id is None:
            raise ValueError('document_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_document_info')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'verbose': verbose
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents/{1}'.format(*self.encode_path_vars(corpus, document_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_document_annotations(self, corpus: str, document_id: str, document_section: str, *, cuis: List[str] = None, include_text: bool = None, **kwargs) -> DetailedResponse:
        """
        Retrieves annotations for a document.

        The response returns a list of all the annotations contained in the document.

        :param str corpus: Corpus name.
        :param str document_id: Document ID.
        :param str document_section: Document section to annotate. (e.g., title,
               abstract, body...
        :param List[str] cuis: (optional) Concepts to show.  Defaults to all
               concepts.
        :param bool include_text: (optional) Include document text.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if document_id is None:
            raise ValueError('document_id must be provided')
        if document_section is None:
            raise ValueError('document_section must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_document_annotations')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'document_section': document_section,
            'cuis': convert_list(cuis),
            'include_text': include_text
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents/{1}/annotations'.format(*self.encode_path_vars(corpus, document_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_document_categories(self, corpus: str, document_id: str, *, highlight_tag_begin: str = None, highlight_tag_end: str = None, types: List[str] = None, category: str = None, only_negated_concepts: bool = None, fields: str = None, limit: int = None, **kwargs) -> DetailedResponse:
        """
        Categorizes concepts in a document.

        The response returns a categorized list of text passages in a document.  The
        sentences are grouped by concept with the matching concepts highlighted.

        :param str corpus: Corpus name.
        :param str document_id: Document ID.
        :param str highlight_tag_begin: (optional) HTML tag used to highlight
               concepts found in the text.  Default is '&ltb&gt'.
        :param str highlight_tag_end: (optional) HTML tag used to highlight
               concepts found in the text.  Default is '&lt/b&gt'.
        :param List[str] types: (optional) Select concepts belonging to these
               semantic types to return. Semantic types for the corpus can be found using
               the /v1/corpora/{corpus}/types method.Defaults to 'all'.
        :param str category: (optional) Select concepts belonging to disorders,
               drugs or genes.
        :param bool only_negated_concepts: (optional) Only return negated
               concepts?.
        :param str fields: (optional) Comma separated list of fields to return:
               passages, annotations, highlightedTitle, highlightedAbstract,
               highlightedBody, highlightedSections.
        :param int limit: (optional) Limit the number of passages per search
               concept (1 to 250).  Default is 50.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CategoriesModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if document_id is None:
            raise ValueError('document_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_document_categories')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'highlight_tag_begin': highlight_tag_begin,
            'highlight_tag_end': highlight_tag_end,
            'types': convert_list(types),
            'category': category,
            'only_negated_concepts': only_negated_concepts,
            '_fields': fields,
            '_limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents/{1}/categories'.format(*self.encode_path_vars(corpus, document_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_doc_multiple_categories(self, corpus: str, document_id: str, categories = None, *, highlight_tag_begin: str = None, highlight_tag_end: str = None, fields: str = None, limit: int = None, **kwargs) -> DetailedResponse:
        """
        Categorizes concepts in a document.

        The response returns multiple categorized lists of text passages in a document.
        The sentences are grouped by concept with the matching concepts
        highlighted.<P>This API should be used to batch multiple categories in a single
        request to improve performance.<P>Example POST body:<pre>{
         categories: [
          {
           name : 'disorders',
           category : 'disorders'
          },
          {
           name : 'drugs',
           category : 'drugs'
          },
          {
           name : 'genes',
           category : 'genes'
          },
          {
           name : 'negated',
           category : 'negated'
          },
          {
           name : 'finding','
           types : ['Finding']
          },
         ]
        }
        </pre>.

        :param str corpus: Corpus name.
        :param str document_id: Document ID.
        :param list[Category] categories:
        :param str highlight_tag_begin: (optional) HTML tag used to highlight
               concepts found in the text.  Default is '&ltb&gt'.
        :param str highlight_tag_end: (optional) HTML tag used to highlight
               concepts found in the text.  Default is '&lt/b&gt'.
        :param str fields: (optional) Comma separated list of fields to return:
               passages, annotations, highlightedTitle, highlightedAbstract,
               highlightedBody, highlightedSections.
        :param int limit: (optional) Limit the number of passages per search
               concept (1 to 250).  Default is 50.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CategoriesModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if document_id is None:
            raise ValueError('document_id must be provided')

        categories = [self._convert_model(x) for x in categories]
        _categories = {}
        _categories['categories'] = categories
        json_string = json.dumps(_categories)

        headers = {
            "content-type": "application/json",
            "Accept": "application/json"
        }
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_document_multiple_categories')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'highlight_tag_begin': highlight_tag_begin,
            'highlight_tag_end': highlight_tag_end,
            '_fields': fields,
            '_limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents/{1}/categories'.format(*self.encode_path_vars(corpus, document_id))
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=json_string)

        response = self.request_iml(request)
        return response


    def get_search_matches(self, corpus: str, document_id: str, min_score: float, *, cuis: List[str] = None, text: List[str] = None, types: List[str] = None, attributes: List[str] = None, values: List[str] = None, nlu_relations: List[str] = None, limit: int = None, search_tag_begin: str = None, search_tag_end: str = None, related_tag_begin: str = None, related_tag_end: str = None, fields: str = None, **kwargs) -> DetailedResponse:
        """
        Finds concepts in a document matching a set of search concepts.

        Returns matching concepts and text passages. The sentences containing each concept
        are returned with the concept highlighted. <p>Extended annotations provide
        additional details for  each discrete search match detected in the document.  An
        iml-annotation-id attribute is added to each highlight tag which allows an
        application to easily show the annotation details when hovering over a text span.
        The iml-annotation-id may also be used to color code the text spans.  The
        ibm_annotation-id is used as a key for the returned annotations. <p>For example, a
        search match on the concept "Breast Carcinoma" will have a class name
        "iml-breast-carcinoma" inserted in the highlight tag, and the returned
        annotations['umls-breast_carcinoma-hypothetical'] JSON field will contain the
        detailed annotation data: <pre>{
         "cui": "C0678222"
         "hypothetical": true
         "preferredName": "Breast Carcinoma"
         "semanticType": "umls.NeoplasticProcess"
         "source": "umls"
         "type": "umls.NeoplasticProcess"
        }
        </pre>.

        :param str corpus: Corpus name.
        :param str document_id: Document ID (e.g, 7014026).
        :param float min_score: Minimum score .0 to 1.0.
        :param List[str] cuis: (optional) cui[,rank,[type]] - Example:
               "C0030567,10". The rank is an optional value from 0 to 10 (defalut is 10).
               Special rank values: 0=omit, 10=require. Related concepts can also be
               included by appending, '-PAR' (parents), '-CHD' (children), or '-SIB'
               (siblings) to the CUI (eg., to include all children of C0030567:
               'C0030567-CHD')).  The type may explicitly select a semanic type for a
               concept.  If no type is specified, a default type is selected.
        :param List[str] text: (optional) Case insensitive text searches.
        :param List[str] types: (optional) Highlight all text spans matching these
               semantic types.  Semantic types for the corpus can be found using the
               /v1/corpora/{corpus}/types method.
        :param List[str] attributes: (optional) Highlight all text spans matching
               these attributes.  An attribute may also specify a range value (e.g.,
               age:years:65-100) or  a string value (e.g., gender:female).  The attribute
               may be qualified with one or more qualifiers (e.g.,
               Treated,Severe>>diabetes)  An attribute may target a specific CUI.  (e.g.,
               C0003864::disease).
        :param List[str] values: (optional) Highlight all text spans matching these
               values.  e.g., age:years:within:65-100 or gender:female  a string value
               (e.g., gender:female).
        :param List[str] nlu_relations: (optional) Highlight all text spans
               matching these NLU relations.  e.g., druggroup,treat,indication.
        :param int limit: (optional) Limit the number of matching passages per
               search concept/search term (1 to 250).  Default is 50.
        :param str search_tag_begin: (optional) HTML tag used to highlight search
               concepts found in the text.  Default is '&ltb&gt'.
        :param str search_tag_end: (optional) HTML tag used to highlight search
               concepts found in the text.  Default is '&lt/b&gt'.
        :param str related_tag_begin: (optional) HTML tag used to highlight related
               concepts found in the text.
        :param str related_tag_end: (optional) HTML tag used to highlight related
               concepts found in the text.
        :param str fields: (optional) Comma separated list of fields to return:
               passages, annotations, highlightedTitle, highlightedAbstract,
               highlightedBody, highlightedSections.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `SearchMatchesModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if document_id is None:
            raise ValueError('document_id must be provided')
        if min_score is None:
            raise ValueError('min_score must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_search_matches')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'min_score': min_score,
            'cuis': convert_list(cuis),
            'text': convert_list(text),
            'types': convert_list(types),
            'attributes': convert_list(attributes),
            'values': convert_list(values),
            'nlu_relations': convert_list(nlu_relations),
            '_limit': limit,
            'search_tag_begin': search_tag_begin,
            'search_tag_end': search_tag_end,
            'related_tag_begin': related_tag_begin,
            'related_tag_end': related_tag_end,
            '_fields': fields
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/documents/{1}/search_matches'.format(*self.encode_path_vars(corpus, document_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response

    #########################
    # Corpora
    #########################


    def get_corpora_config(self, *, verbose: bool = None, **kwargs) -> DetailedResponse:
        """
        Retrieves the available corpus names and configuration.

        The response returns an array of available corpus names and optionally includes
        detailed configuation parameters.

        :param bool verbose: (optional) Verbose output.  Default verbose = false.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorporaConfig` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_corpora_config')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'verbose': verbose
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def set_corpus_schema(self, *, enrichment_targets: List[object] = None, metadata_fields: List[object] = None, corpus_name: str = None, references: dict = None, **kwargs) -> DetailedResponse:
        """
        Define service repository data model.

        The response returns whether the instance schema was properly created.  <P>This
        API should be used for defining a custom corpus schema.<P>Example POST body:<pre>{
           corpusName : 'string'
          "enrichmentTargets" : [
           {
            "contentField": 'string',
            "enrichmentField : 'string'
           }
          ],
          "metadataFields" : [
           {
            "fieldName": 'string',
            "fieldType : 'string'
           }
          ],
          "referenceIndices" : {
           "dictionaryIndex" : "my_umls",
           "attributeIndex" : "my_attributes",
           "meshIndex" : "my_mesh",
          }
        }
        </pre>.

        :param List[object] enrichment_targets: (optional) Input and Output field
               names.
        :param List[object] metadata_fields: (optional) Metadata field names.
        :param str corpus_name: (optional) Corpus name.
        :param dict references: (optional) Reference indices.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorporaConfig` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='set_corpus_schema')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'enrichmentTargets': enrichment_targets,
            'metadataFields': metadata_fields,
            'corpusName': corpus_name,
            'references': references
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_iml(request)
        return response


    def delete_corpus_schema(self, instance: str, **kwargs) -> DetailedResponse:
        """
        Delete a corpus.

        The response returns whether the instance schema was properly deleted.

        :param str instance: corpus schema.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorporaConfig` object
        """

        if instance is None:
            raise ValueError('instance must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='delete_corpus_schema')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'instance': instance
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora'
        request = self.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def set_corpus_config(self, *, user_name: str = None, password: str = None, corpus_uri: str = None, **kwargs) -> DetailedResponse:
        """
        Define service repository.

        The response returns whether the service successfully connected to the specified
        repository.  <P>This API should be used for providing a custom enriched
        corpus.<P>Example POST body:<pre>{
           userName : 'string',
           password : 'string'
           repositoryUri : 'uri'
        }
        </pre>.

        :param str user_name: (optional) Repository connection userid.
        :param str password: (optional) Repository connection password.
        :param str corpus_uri: (optional) Repository connection URI.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorporaConfig` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='set_corpus_config')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'userName': user_name,
            'password': password,
            'corpusURI': corpus_uri
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/configure'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_iml(request)
        return response


    def monitor_corpus(self, apikey: str, **kwargs) -> DetailedResponse:
        """
        Enable monitoring for a custom instance.

        This API is meant to be used for IBM Cloud automated monitoring of custom plan
        instances.  A service api-key with read only role can be submitted to enable
        monitoring.

        :param str apikey: Apikey with read only permissions for monitoring.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if apikey is None:
            raise ValueError('apikey must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='monitor_corpus')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'apikey': apikey
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/monitor'
        request = self.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def enable_corpus_search_tracking(self, *, enable_tracking: bool = None, **kwargs) -> DetailedResponse:
        """
        Toggle Search Activity Tracking.

        The response returns whether the tracking was enabled or disabled.

        :param bool enable_tracking: (optional) Enable corpus read event tracking.
               Default is false.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='enable_corpus_search_tracking')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'enable_tracking': enable_tracking
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/tracking'
        request = self.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_corpus_config(self, corpus: str, *, verbose: bool = None, **kwargs) -> DetailedResponse:
        """
        Retrieves the corpus configuration.

        The response returns the corpus configuration.

        :param str corpus: Corpus name.
        :param bool verbose: (optional) Verbose output.  Default verbose = false.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `CorporaConfig` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_corpus_config')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'verbose': verbose
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    #########################
    # Status
    #########################


    def get_health_check_status(self, *, accept: str = None, format: str = None, **kwargs) -> DetailedResponse:
        """
        Determine if service is running correctly.

        This resource differs from /status in that it will will always return a 500 error
        if the service state is not OK.  This makes it simpler for service front ends
        (such as Datapower) to detect a failed service.

        :param str accept: (optional) The type of the response: application/json or
               application/xml.
        :param str format: (optional) Override response format.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ServiceStatus` object
        """

        headers = {
            'Accept': accept
        }
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_health_check_status')
        headers.update(sdk_headers)

        params = {
            'format': format
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/status/health_check'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response

    #########################
    # Search
    #########################


    def search(self, corpus: str, returns: dict = None, *, query = None, verbose: bool = None, **kwargs) -> DetailedResponse:
        """
        Search for concepts, documents, and authors.

        Features include:<ul><li>Concept search</li><li>Keyword search</li><li>Attributes
        search</li><li>Attributes typeahead</li><li>Regular expressions</li><li>Find
        passages</li><li>Selecting authors</li><li>Selecting providers</li><li>Date
        ranges: publish date</li><li>Pagination</li><li>Aggregation: authors, concepts,
        and documents</li><li>Document date histogram</li></ul>.

        :param str corpus: Corpus name.
        :param dict returns: Search definition - must include a returns data block
        :param bool verbose: (optional) Verbose output.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `SearchModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if query is not None:
            query = self._convert_model(query)
        if returns is None:
            raise ValueError('returns must be provided')
        else:
            returns = self._convert_model(returns)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='search')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'verbose': verbose
        }

        data = {
            "query": query,
            "returns": returns
        }
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        json_string = json.dumps(data, indent=2, cls=SearchableConceptEncoder)

        url = '/v1/corpora/{0}/search'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=json_string)

        response = self.send(request)
        return response


    def get_fields(self, corpus: str, **kwargs) -> DetailedResponse:
        """
        Retrieves a list of metadata fields defined in the corpus.

        The response returns a list of metadata field names that can be used by the POST
        search API.

        :param str corpus: Corpus name.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `MetadataModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_fields')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/search/metadata'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def typeahead(self, corpus: str, query: str, *, ontologies: List[str] = None, types: List[str] = None, category: str = None, verbose: bool = None, limit: int = None, max_hit_count: int = None, no_duplicates: bool = None, **kwargs) -> DetailedResponse:
        """
        Find concepts matching the specified query string.

        Searches concepts mentioned in the corpus looking for matches on the query string
        field. The comparison is not case sensitive. The main use of this method is to
        build query boxes that offer auto-complete, to allow users to select valid
        concepts.

        :param str corpus: Comma-separated corpora names.
        :param str query: Query string.
        :param List[str] ontologies: (optional) Include suggestions belonging to
               the selected ontology(ies).
        :param List[str] types: (optional) Include or exclude suggestions belonging
               to one of these types.  Types can be found using /v1/corpora/{corpus}/types
               method.  Defaults to all.
        :param str category: (optional) Select concepts belonging to disorders,
               drugs or genes.
        :param bool verbose: (optional) Verbose output.  Include hit counts and
               relationship counts for each concept.
        :param int limit: (optional) Maximum number of suggestions to return.
        :param int max_hit_count: (optional) Maximum hit (document) count for
               suggested concepts. Default is 500000.  High hit count concepts tend to be
               very broad (e.g, Disease) and result in longer search times.
        :param bool no_duplicates: (optional) Remove duplicate concepts.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ConceptListModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if query is None:
            raise ValueError('query must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='typeahead')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'query': query,
            'ontologies': convert_list(ontologies),
            'types': convert_list(types),
            'category': category,
            'verbose': verbose,
            '_limit': limit,
            'max_hit_count': max_hit_count,
            'no_duplicates': no_duplicates
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/search/typeahead'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response

    #########################
    # Concepts
    #########################


    def get_concepts(self, corpus: str, *, cuis: List[str] = None, preferred_names: List[str] = None, surface_forms: List[str] = None, attributes: List[str] = None, verbose: bool = None, sort: str = None, limit: int = None, **kwargs) -> DetailedResponse:
        """
        Retrieves information for concepts mentioned in this corpus.

        The response returns concepts mentioned in this corpus.  The returned concepts may
        be selected by CUI, preferred name, suface forms and attribute name.  All selected
        concepts are returned.

        :param str corpus: Corpus name.
        :param List[str] cuis: (optional) Select concepts with the specified CUIs.
               Each cui is assumed to be from UMLS unless an ontology is explicitly
               specified using the syntax [ontology:]cui, e.g., 'concepts:C0018787'.
        :param List[str] preferred_names: (optional) Select concepts with the
               specified preferred names. Each preferred name is assumed to be from UMLS
               unless an ontology is explicitly specified using the syntax
               [ontology:::]preferred_name, e.g., 'concepts:::HEART'.
        :param List[str] surface_forms: (optional) Select all concepts having these
               surface forms. The match is case insensitive. Each surface form is matched
               against UMLS unless an ontology is explicitly specified using the syntax
               [ontology:::]surface_form, e.g., 'concepts:::heart attack'.
        :param List[str] attributes: (optional) Select all concepts having these
               attributes. The match is case insensitive.
        :param bool verbose: (optional) Verbose output.  Default is false.
        :param str sort: (optional) Sort by hitCount (in document count).  Set to
               ascending order (_sort=+hitCount) or descending order (_sort=-hitCount).
        :param int limit: (optional) Number of possible concepts to return. Default
               is 250.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ConceptListModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_concepts')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'cuis': convert_list(cuis),
            'preferred_names': convert_list(preferred_names),
            'surface_forms': convert_list(surface_forms),
            'attributes': convert_list(attributes),
            'verbose': verbose,
            '_sort': sort,
            '_limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def add_artifact(self, corpus: str, *, dictionary_entry: 'DictonaryEntry' = None, attribute_entry: 'AttributeEntry' = None, **kwargs) -> DetailedResponse:
        """
        Add cartridge artifact.

        :param str corpus: Corpus name.
        :param DictonaryEntry dictionary_entry: (optional)
        :param AttributeEntry attribute_entry: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if dictionary_entry is not None:
            dictionary_entry = convert_model(dictionary_entry)
        if attribute_entry is not None:
            attribute_entry = convert_model(attribute_entry)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='add_artifact')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'dictionaryEntry': dictionary_entry,
            'attributeEntry': attribute_entry
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts/definitions'.format(*self.encode_path_vars(corpus))
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_iml(request)
        return response


    def get_cui_info(self, corpus: str, name_or_id: str, *, ontology: str = None, fields: str = None, tree_layout: bool = None, **kwargs) -> DetailedResponse:
        """
        Retrieve information for a concept.

        The followning fields may be retrieved: <ul><li>Preferred name</li><li>Semantic
        types</li><li>Surface forms - Ontology Dictionary names for this
        concept</li><li>Definition - Concept definition (if available)</li><li>Related
        Concepts info</li></ul><P>The default is to return all fields.  Individual fields
        may be selected using the '_fields' query parameter.

        :param str corpus: Corpus name.
        :param str name_or_id: Preferred name or concept ID.
        :param str ontology: (optional) The ontology that defines the cui.
        :param str fields: (optional) Comma separated list of fields to return:
               preferredName, semanticTypes, surfaceForms, typeahead, variants,
               definition.  Defaults to all fields.
        :param bool tree_layout: (optional) Generate JSON output that is compatible
               with a d3 tree layout.  Default is false.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ConceptInfoModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if name_or_id is None:
            raise ValueError('name_or_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_cui_info')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'ontology': ontology,
            '_fields': fields,
            'tree_layout': tree_layout
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts/{1}'.format(*self.encode_path_vars(corpus, name_or_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_hit_count(self, corpus: str, name_or_id: str, *, ontology: str = None, **kwargs) -> DetailedResponse:
        """
        Retrieves a count of the number of times a concept is mentioned in the corpus.

        The response returns the number of times a concept is mentioned (hit count) in the
        corpus.

        :param str corpus: Corpus name.
        :param str name_or_id: Preferred name or concept ID.
        :param str ontology: (optional) The ontology that defines the cui.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `HitCount` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if name_or_id is None:
            raise ValueError('name_or_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_hit_count')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'ontology': ontology
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts/{1}/hit_count'.format(*self.encode_path_vars(corpus, name_or_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_related_concepts(self, corpus: str, name_or_id: str, relationship: str, *, ontology: str = None, relationship_attributes: List[str] = None, sources: List[str] = None, recursive: bool = None, tree_layout: bool = None, max_depth: int = None, **kwargs) -> DetailedResponse:
        """
        Retrieve concepts related to a concept.

        Returns a list of related concepts mentioned in the specified corpus. The
        following relationships are suppored: <ul><li><b>children</b> child
        concepts</li><li><b>parents</b> parent concepts</li><li><b>siblings</b> sibling
        concepts</li><li><b>synonyms</b> synonym concepts</li><li><b>qualified by</b>
        qualified by concepts</li><li><b>broader</b> broader
        concepts</li><li><b>narrower</b> narrower concepts</li><li><b>other</b> other than
        synonyms, narrower or broader</li><li><b>related</b> related and posibly
        synonymous concepts</li></ul><p>If the corpus path parameter can be set to 'umls'
        to look up relationship in the entire UMLS dictionary.  Otherwise, an actual
        corpus name may be specified to limit the output to only those concepts mentioned
        in a specific corpus.

        :param str corpus: Corpus name or null to show all ontology relationships.
        :param str name_or_id: Preferred name or concept ID.
        :param str relationship: Select the relationship to retrieve.
        :param str ontology: (optional) The ontology that defines the cui.
        :param List[str] relationship_attributes: (optional) Select UMLS
               relationship attributes.  If null, all relationship attributes are
               returned.
        :param List[str] sources: (optional) Select source vocabularies.  If null,
               concepts for all source vocabularies are returned.
        :param bool recursive: (optional) Recursively return parents, children,
               broader and narrower relations.  Default is false.
        :param bool tree_layout: (optional) Generate JSON output that is compatible
               with a d3 tree layout.  Default is true.
        :param int max_depth: (optional) Maximum depth.  Default is 3.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `RelatedConceptsModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if name_or_id is None:
            raise ValueError('name_or_id must be provided')
        if relationship is None:
            raise ValueError('relationship must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_related_concepts')
        headers.update(sdk_headers)

        params = {
            'relationship': relationship,
            'version': self.version,
            'ontology': ontology,
            'relationship_attributes': convert_list(relationship_attributes),
            'sources': convert_list(sources),
            'recursive': recursive,
            'tree_layout': tree_layout,
            'max_depth': max_depth
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts/{1}/related_concepts'.format(*self.encode_path_vars(corpus, name_or_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


    def get_similar_concepts(self, corpus: str, name_or_id: str, return_ontologies: List[str], *, ontology: str = None, limit: int = None, **kwargs) -> DetailedResponse:
        """
        Find similar concepts.

        The response returns a list of similar concepts.   All ontologies defined in the
        corpora are searched.  Similarity is determined by checking for overlapping
        surface forms.  The results are sorted in descending order by hit count.

        :param str corpus: Corpus name.
        :param str name_or_id: Preferred name or concept ID.
        :param List[str] return_ontologies: Return similar concepts from any of
               these ontologites.
        :param str ontology: (optional) The ontology that defines the cui.
        :param int limit: (optional) Number of possible concepts to return. Default
               is 250.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ConceptListModel` object
        """

        if corpus is None:
            raise ValueError('corpus must be provided')
        if name_or_id is None:
            raise ValueError('name_or_id must be provided')
        if return_ontologies is None:
            raise ValueError('return_ontologies must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_similar_concepts')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'return_ontologies': convert_list(return_ontologies),
            'ontology': ontology,
            '_limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/corpora/{0}/concepts/{1}/similar_concepts'.format(*self.encode_path_vars(corpus, name_or_id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_iml(request)
        return response


class GetDocumentCategoriesEnums:
    """
    Enums for get_document_categories parameters.
    """

    class Category(Enum):
        """
        Select concepts belonging to disorders, drugs or genes.
        """
        DISORDERS = 'disorders'
        DRUGS = 'drugs'
        GENES = 'genes'


class GetServiceStatusEnums:
    """
    Enums for get_service_status parameters.
    """

    class Accept(Enum):
        """
        The type of the response: application/json or application/xml.
        """
        APPLICATION_JSON = 'application/json'
        APPLICATION_XML = 'application/xml'
    class Format(Enum):
        """
        Override response format.
        """
        JSON = 'json'
        XML = 'xml'
    class LivenessCheck(Enum):
        """
        Perform a shallow liveness check.
        """
        TRUE = 'true'
        FALSE = 'false'


class GetHealthCheckStatusEnums:
    """
    Enums for get_health_check_status parameters.
    """

    class Accept(Enum):
        """
        The type of the response: application/json or application/xml.
        """
        APPLICATION_JSON = 'application/json'
        APPLICATION_XML = 'application/xml'
    class Format(Enum):
        """
        Override response format.
        """
        JSON = 'json'
        XML = 'xml'


class TypeaheadEnums:
    """
    Enums for typeahead parameters.
    """

    class Ontologies(Enum):
        """
        Include suggestions belonging to the selected ontology(ies).
        """
        CONCEPTS = 'concepts'
        MESH = 'mesh'
    class Category(Enum):
        """
        Select concepts belonging to disorders, drugs or genes.
        """
        DISORDERS = 'disorders'
        DRUGS = 'drugs'
        GENES = 'genes'


class GetRelatedConceptsEnums:
    """
    Enums for get_related_concepts parameters.
    """

    class Relationship(Enum):
        """
        Select the relationship to retrieve.
        """
        CHILDREN = 'children'
        PARENTS = 'parents'
        SIBLINGS = 'siblings'
        ALLOWEDQUALIFIER = 'allowedQualifier'
        QUALIFIEDBY = 'qualifiedBy'
        BROADER = 'broader'
        ALIKE = 'alike'
        NARROWER = 'narrower'
        OTHER = 'other'
        RELATEDUNSPECIFIED = 'relatedUnspecified'
        RELATED = 'related'
        SYNONYM = 'synonym'
        NOTRELATED = 'notRelated'
        CHD = 'chd'
        PAR = 'par'
        SIB = 'sib'
        AQ = 'aq'
        QB = 'qb'
        RB = 'rb'
        RL = 'rl'
        RN = 'rn'
        RO = 'ro'
        RU = 'ru'
        RQ = 'rq'
        SY = 'sy'
        XR = 'xr'


class TokenizeEnums:
    """
    Enums for tokenize parameters.
    """

    class Ontologies(Enum):
        """
        Detect artifacts in the selected ontology(ies).
        """
        MESH = 'mesh'
        CONCEPTS = 'concepts'


##############################################################################
# Models
##############################################################################


class AggregationModel(object):
    """
    Model for field aggregations.
    :attr str name: (optional) Name of the aggregation.
    :attr int document_count: (optional) Corpus frequency of the aggregation.
    """

    def __init__(self, name=None, document_count=None):
        """
        Initialize a AggregationModel object.
        :param str name: (optional) Name of the aggregation.
        :param int document_count: (optional) Corpus frequency of the aggregation.
        """
        self.name = name
        self.document_count = document_count

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'documentCount' in _dict:
            args['document_count'] = _dict.get('documentCount')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'document_count') and self.document_count is not None:
            _dict['documentCount'] = self.document_count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this AggregationModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AggregationModel():
    """
    Model for field aggregations.

    :attr str name: (optional) Name of the aggregation.
    :attr int document_count: (optional) Corpus frequency of the aggregation.
    """

    def __init__(self, *, name: str = None, document_count: int = None) -> None:
        """
        Initialize a AggregationModel object.

        :param str name: (optional) Name of the aggregation.
        :param int document_count: (optional) Corpus frequency of the aggregation.
        """
        self.name = name
        self.document_count = document_count

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AggregationModel':
        """Initialize a AggregationModel object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'documentCount' in _dict:
            args['document_count'] = _dict.get('documentCount')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'document_count') and self.document_count is not None:
            _dict['documentCount'] = self.document_count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AggregationModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AggregationModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AggregationModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Aggregations(object):
    """
    Aggregations.
    :attr int limit: (optional)
    """

    def __init__(self, limit=None):
        """
        Initialize a Aggregations object.
        :param int limit: (optional)
        """
        self.limit = limit

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Aggregations object from a json dictionary."""
        args = {}
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Aggregations object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AnnotationModel(object):
    """
    Model for congntive asset annotations.
    :attr int unique_id: (optional) Unique identifer of annotation.
    :attr list[int] sticky_ids: (optional) List of identifiers associated with annotation.
    :attr str ontology: (optional) Source ontology of annotation.
    :attr str section: (optional) Document section for annotation.
    :attr str preferred_name: (optional) Ontology provide normalized name of annotation.
    :attr str cui: (optional) Ontology provided unique identifier of annotation.
    :attr str attribute_id: (optional) Attribute identifier of annotation.
    :attr list[str] qualifiers: (optional) Qualifier for attribute annotation.
    :attr str type: (optional) Ontology provided semantic type of annotation.
    :attr bool negated: (optional) Whether the annotation is a negated span.
    :attr bool hypothetical: (optional) Whether the annotation is a hypothetical span.
    :attr str unit: (optional) Unit of measure for attribute value annotation.
    :attr str min_value: (optional) Minumum value for attribute value annotation.
    :attr str max_value: (optional) Maximum value for attribute value annotation.
    :attr str operator: (optional) Mathematical operator for attribute value annotation.
    :attr str nlu_source_type: (optional) Ontology type of source relation annotation.
    :attr str nlu_relation: (optional) Relation name for annotation.
    :attr str nlu_target_type: (optional) Ontology type of target relation annotation.
    :attr str nlu_entity_index: (optional)
    :attr str nlu_mention_index: (optional)
    :attr str nlu_relation_id: (optional)
    :attr str nlu_side: (optional)
    :attr int begin: (optional) Starting offset of annotation.
    :attr int end: (optional) Ending offset of annotation.
    :attr float score: (optional) Relevancy score of annotation.
    :attr int timestamp: (optional)
    :attr dict features: (optional)
    :attr int hits: (optional) Number of times artifact is mentioned in the corpus.
    """

    def __init__(self, unique_id=None, sticky_ids=None, ontology=None, section=None,
                 preferred_name=None, cui=None, attribute_id=None, qualifiers=None, type=None,
                 negated=None, hypothetical=None, unit=None, min_value=None, max_value=None,
                 operator=None, nlu_source_type=None, nlu_relation=None, nlu_target_type=None,
                 nlu_entity_index=None, nlu_mention_index=None, nlu_relation_id=None, nlu_side=None,
                 begin=None, end=None, score=None, timestamp=None, features=None, hits=None):
        """
        Initialize a AnnotationModel object.
        :param int unique_id: (optional) Unique identifer of annotation.
        :param list[int] sticky_ids: (optional) List of identifiers associated with
        annotation.
        :param str ontology: (optional) Source ontology of annotation.
        :param str section: (optional) Document section for annotation.
        :param str preferred_name: (optional) Ontology provide normalized name of
        annotation.
        :param str cui: (optional) Ontology provided unique identifier of annotation.
        :param str attribute_id: (optional) Attribute identifier of annotation.
        :param list[str] qualifiers: (optional) Qualifier for attribute annotation.
        :param str type: (optional) Ontology provided semantic type of annotation.
        :param bool negated: (optional) Whether the annotation is a negated span.
        :param bool hypothetical: (optional) Whether the annotation is a hypothetical
        span.
        :param str unit: (optional) Unit of measure for attribute value annotation.
        :param str min_value: (optional) Minumum value for attribute value annotation.
        :param str max_value: (optional) Maximum value for attribute value annotation.
        :param str operator: (optional) Mathematical operator for attribute value
        annotation.
        :param str nlu_source_type: (optional) Ontology type of source relation
        annotation.
        :param str nlu_relation: (optional) Relation name for annotation.
        :param str nlu_target_type: (optional) Ontology type of target relation
        annotation.
        :param str nlu_entity_index: (optional)
        :param str nlu_mention_index: (optional)
        :param str nlu_relation_id: (optional)
        :param str nlu_side: (optional)
        :param int begin: (optional) Starting offset of annotation.
        :param int end: (optional) Ending offset of annotation.
        :param float score: (optional) Relevancy score of annotation.
        :param int timestamp: (optional)
        :param dict features: (optional)
        :param int hits: (optional) Number of times artifact is mentioned in the corpus.
        """
        self.unique_id = unique_id
        self.sticky_ids = sticky_ids
        self.ontology = ontology
        self.section = section
        self.preferred_name = preferred_name
        self.cui = cui
        self.attribute_id = attribute_id
        self.qualifiers = qualifiers
        self.type = type
        self.negated = negated
        self.hypothetical = hypothetical
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.operator = operator
        self.nlu_source_type = nlu_source_type
        self.nlu_relation = nlu_relation
        self.nlu_target_type = nlu_target_type
        self.nlu_entity_index = nlu_entity_index
        self.nlu_mention_index = nlu_mention_index
        self.nlu_relation_id = nlu_relation_id
        self.nlu_side = nlu_side
        self.begin = begin
        self.end = end
        self.score = score
        self.timestamp = timestamp
        self.features = features
        self.hits = hits

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AnnotationModel object from a json dictionary."""
        args = {}
        if 'uniqueId' in _dict:
            args['unique_id'] = _dict.get('uniqueId')
        if 'stickyIds' in _dict:
            args['sticky_ids'] = _dict.get('stickyIds')
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'section' in _dict:
            args['section'] = _dict.get('section')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'attributeId' in _dict:
            args['attribute_id'] = _dict.get('attributeId')
        if 'qualifiers' in _dict:
            args['qualifiers'] = _dict.get('qualifiers')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'negated' in _dict:
            args['negated'] = _dict.get('negated')
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict.get('hypothetical')
        if 'unit' in _dict:
            args['unit'] = _dict.get('unit')
        if 'minValue' in _dict:
            args['min_value'] = _dict.get('minValue')
        if 'maxValue' in _dict:
            args['max_value'] = _dict.get('maxValue')
        if 'operator' in _dict:
            args['operator'] = _dict.get('operator')
        if 'nluSourceType' in _dict:
            args['nlu_source_type'] = _dict.get('nluSourceType')
        if 'nluRelation' in _dict:
            args['nlu_relation'] = _dict.get('nluRelation')
        if 'nluTargetType' in _dict:
            args['nlu_target_type'] = _dict.get('nluTargetType')
        if 'nluEntityIndex' in _dict:
            args['nlu_entity_index'] = _dict.get('nluEntityIndex')
        if 'nluMentionIndex' in _dict:
            args['nlu_mention_index'] = _dict.get('nluMentionIndex')
        if 'nluRelationId' in _dict:
            args['nlu_relation_id'] = _dict.get('nluRelationId')
        if 'nluSide' in _dict:
            args['nlu_side'] = _dict.get('nluSide')
        if 'begin' in _dict:
            args['begin'] = _dict.get('begin')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        if 'score' in _dict:
            args['score'] = _dict.get('score')
        if 'timestamp' in _dict:
            args['timestamp'] = _dict.get('timestamp')
        if 'features' in _dict:
            args['features'] = _dict.get('features')
        if 'hits' in _dict:
            args['hits'] = _dict.get('hits')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unique_id') and self.unique_id is not None:
            _dict['uniqueId'] = self.unique_id
        if hasattr(self, 'sticky_ids') and self.sticky_ids is not None:
            _dict['stickyIds'] = self.sticky_ids
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'section') and self.section is not None:
            _dict['section'] = self.section
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'attribute_id') and self.attribute_id is not None:
            _dict['attributeId'] = self.attribute_id
        if hasattr(self, 'qualifiers') and self.qualifiers is not None:
            _dict['qualifiers'] = self.qualifiers
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'min_value') and self.min_value is not None:
            _dict['minValue'] = self.min_value
        if hasattr(self, 'max_value') and self.max_value is not None:
            _dict['maxValue'] = self.max_value
        if hasattr(self, 'operator') and self.operator is not None:
            _dict['operator'] = self.operator
        if hasattr(self, 'nlu_source_type') and self.nlu_source_type is not None:
            _dict['nluSourceType'] = self.nlu_source_type
        if hasattr(self, 'nlu_relation') and self.nlu_relation is not None:
            _dict['nluRelation'] = self.nlu_relation
        if hasattr(self, 'nlu_target_type') and self.nlu_target_type is not None:
            _dict['nluTargetType'] = self.nlu_target_type
        if hasattr(self, 'nlu_entity_index') and self.nlu_entity_index is not None:
            _dict['nluEntityIndex'] = self.nlu_entity_index
        if hasattr(self, 'nlu_mention_index') and self.nlu_mention_index is not None:
            _dict['nluMentionIndex'] = self.nlu_mention_index
        if hasattr(self, 'nlu_relation_id') and self.nlu_relation_id is not None:
            _dict['nluRelationId'] = self.nlu_relation_id
        if hasattr(self, 'nlu_side') and self.nlu_side is not None:
            _dict['nluSide'] = self.nlu_side
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = self.timestamp
        if hasattr(self, 'features') and self.features is not None:
            _dict['features'] = self.features
        if hasattr(self, 'hits') and self.hits is not None:
            _dict['hits'] = self.hits
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this AnnotationModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ArtifactModel(object):
    """
    Model for ontology artifact.
    :attr str cui: (optional) Ontology provided unique identifier for artifact.
    :attr str ontology: (optional) Source ontology for artifact.
    :attr str preferred_name: (optional) Ontology provided normalized name for artifact.
    :attr str alternative_name: (optional) Ontology provided alternative name for
    artifact.
    :attr str type: (optional) Ontology semantic type for artifact.
    :attr int rank: (optional) Search weight assigned to artifact.
    :attr int hit_count: (optional) Number of corpus documents artifact was found in.
    :attr float score: (optional) Relevance score for artifact.
    :attr list[str] surface_forms: (optional) List of artifact synonyms.
    """

    def __init__(self, cui=None, ontology=None, preferred_name=None, alternative_name=None,
                 type=None, rank=None, hit_count=None, score=None, surface_forms=None):
        """
        Initialize a ArtifactModel object.
        :param str cui: (optional) Ontology provided unique identifier for artifact.
        :param str ontology: (optional) Source ontology for artifact.
        :param str preferred_name: (optional) Ontology provided normalized name for
        artifact.
        :param str alternative_name: (optional) Ontology provided alternative name for
        artifact.
        :param str type: (optional) Ontology semantic type for artifact.
        :param int rank: (optional) Search weight assigned to artifact.
        :param int hit_count: (optional) Number of corpus documents artifact was found in.
        :param float score: (optional) Relevance score for artifact.
        :param list[str] surface_forms: (optional) List of artifact synonyms.
        """
        self.cui = cui
        self.ontology = ontology
        self.preferred_name = preferred_name
        self.alternative_name = alternative_name
        self.type = type
        self.rank = rank
        self.hit_count = hit_count
        self.score = score
        self.surface_forms = surface_forms

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ArtifactModel object from a json dictionary."""
        args = {}
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'alternativeName' in _dict:
            args['alternative_name'] = _dict.get('alternativeName')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'rank' in _dict:
            args['rank'] = _dict.get('rank')
        if 'hitCount' in _dict:
            args['hit_count'] = _dict.get('hitCount')
        if 'score' in _dict:
            args['score'] = _dict.get('score')
        if 'surfaceForms' in _dict:
            args['surface_forms'] = _dict.get('surfaceForms')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'alternative_name') and self.alternative_name is not None:
            _dict['alternativeName'] = self.alternative_name
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'rank') and self.rank is not None:
            _dict['rank'] = self.rank
        if hasattr(self, 'hit_count') and self.hit_count is not None:
            _dict['hitCount'] = self.hit_count
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'surface_forms') and self.surface_forms is not None:
            _dict['surfaceForms'] = self.surface_forms
        return _dict

    def __str__(self):
        """Return a `str` version of this ArtifactModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Attribute(object):
    """
    Object representing an attribute artifact.
    :attr str attribute_id: (optional) Unique identifier for attribute artifact.
    :attr str display_name: (optional) Display name for attribute artifact.
    :attr int count: (optional) Corpus frequency for attribute artifact.
    """

    def __init__(self, attribute_id=None, display_name=None, count=None):
        """
        Initialize a Attribute object.
        :param str attribute_id: (optional) Unique identifier for attribute artifact.
        :param str display_name: (optional) Display name for attribute artifact.
        :param int count: (optional) Corpus frequency for attribute artifact.
        """
        self.attribute_id = attribute_id
        self.display_name = display_name
        self.count = count

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Attribute object from a json dictionary."""
        args = {}
        if 'attributeId' in _dict:
            args['attribute_id'] = _dict.get('attributeId')
        if 'displayName' in _dict:
            args['display_name'] = _dict.get('displayName')
        if 'count' in _dict:
            args['count'] = _dict.get('count')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'attribute_id') and self.attribute_id is not None:
            _dict['attributeId'] = self.attribute_id
        if hasattr(self, 'display_name') and self.display_name is not None:
            _dict['displayName'] = self.display_name
        if hasattr(self, 'count') and self.count is not None:
            _dict['count'] = self.count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Attribute object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AttributeEntry():
    """
    AttributeEntry.

    :attr str attr_name: (optional)
    :attr str data_type: (optional)
    :attr str default_value: (optional)
    :attr str description: (optional)
    :attr str display_name: (optional)
    :attr str doc_id: (optional)
    :attr List[str] field_values: (optional)
    :attr str maximum_value: (optional)
    :attr str minimum_value: (optional)
    :attr bool multi_value: (optional)
    :attr str units: (optional)
    :attr str value_type: (optional)
    :attr List[PossbileValues] possible_values: (optional)
    """

    def __init__(self, *, attr_name: str = None, data_type: str = None, default_value: str = None, description: str = None, display_name: str = None, doc_id: str = None, field_values: List[str] = None, maximum_value: str = None, minimum_value: str = None, multi_value: bool = None, units: str = None, value_type: str = None, possible_values: List['PossbileValues'] = None) -> None:
        """
        Initialize a AttributeEntry object.

        :param str attr_name: (optional)
        :param str data_type: (optional)
        :param str default_value: (optional)
        :param str description: (optional)
        :param str display_name: (optional)
        :param str doc_id: (optional)
        :param List[str] field_values: (optional)
        :param str maximum_value: (optional)
        :param str minimum_value: (optional)
        :param bool multi_value: (optional)
        :param str units: (optional)
        :param str value_type: (optional)
        :param List[PossbileValues] possible_values: (optional)
        """
        self.attr_name = attr_name
        self.data_type = data_type
        self.default_value = default_value
        self.description = description
        self.display_name = display_name
        self.doc_id = doc_id
        self.field_values = field_values
        self.maximum_value = maximum_value
        self.minimum_value = minimum_value
        self.multi_value = multi_value
        self.units = units
        self.value_type = value_type
        self.possible_values = possible_values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AttributeEntry':
        """Initialize a AttributeEntry object from a json dictionary."""
        args = {}
        if 'attr_name' in _dict:
            args['attr_name'] = _dict.get('attr_name')
        if 'data_type' in _dict:
            args['data_type'] = _dict.get('data_type')
        if 'default_value' in _dict:
            args['default_value'] = _dict.get('default_value')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'display_name' in _dict:
            args['display_name'] = _dict.get('display_name')
        if 'doc_id' in _dict:
            args['doc_id'] = _dict.get('doc_id')
        if 'field_values' in _dict:
            args['field_values'] = _dict.get('field_values')
        if 'maximum_value' in _dict:
            args['maximum_value'] = _dict.get('maximum_value')
        if 'minimum_value' in _dict:
            args['minimum_value'] = _dict.get('minimum_value')
        if 'multi_value' in _dict:
            args['multi_value'] = _dict.get('multi_value')
        if 'units' in _dict:
            args['units'] = _dict.get('units')
        if 'valueType' in _dict:
            args['value_type'] = _dict.get('valueType')
        if 'possible_values' in _dict:
            args['possible_values'] = [PossibleValues.from_dict(x) for x in _dict.get('possible_values')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AttributeEntry object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'attr_name') and self.attr_name is not None:
            _dict['attr_name'] = self.attr_name
        if hasattr(self, 'data_type') and self.data_type is not None:
            _dict['data_type'] = self.data_type
        if hasattr(self, 'default_value') and self.default_value is not None:
            _dict['default_value'] = self.default_value
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'display_name') and self.display_name is not None:
            _dict['display_name'] = self.display_name
        if hasattr(self, 'doc_id') and self.doc_id is not None:
            _dict['doc_id'] = self.doc_id
        if hasattr(self, 'field_values') and self.field_values is not None:
            _dict['field_values'] = self.field_values
        if hasattr(self, 'maximum_value') and self.maximum_value is not None:
            _dict['maximum_value'] = self.maximum_value
        if hasattr(self, 'minimum_value') and self.minimum_value is not None:
            _dict['minimum_value'] = self.minimum_value
        if hasattr(self, 'multi_value') and self.multi_value is not None:
            _dict['multi_value'] = self.multi_value
        if hasattr(self, 'units') and self.units is not None:
            _dict['units'] = self.units
        if hasattr(self, 'value_type') and self.value_type is not None:
            _dict['valueType'] = self.value_type
        if hasattr(self, 'possible_values') and self.possible_values is not None:
            _dict['possible_values'] = [x.to_dict() for x in self.possible_values]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AttributeEntry object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AttributeEntry') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AttributeEntry') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Attributes(object):
    """
    Attributes.
    """

    def __init__(self, **kwargs):
        """
        Initialize a Attributes object.
        :param **kwargs: (optional) Any additional properties.
        """
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Attributes object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {}
        if not hasattr(self, '_additionalProperties'):
            super(Attributes, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Attributes, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Attributes object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Backend():
    """
    Object representing repository response.

    :attr List[Message] messages: (optional) Repository messages.
    """

    def __init__(self, *, messages: List['Message'] = None) -> None:
        """
        Initialize a Backend object.

        :param List[Message] messages: (optional) Repository messages.
        """
        self.messages = messages

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Backend':
        """Initialize a Backend object from a json dictionary."""
        args = {}
        if 'messages' in _dict:
            args['messages'] = [Message.from_dict(x) for x in _dict.get('messages')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Backend object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'messages') and self.messages is not None:
            _dict['messages'] = [x.to_dict() for x in self.messages]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Backend object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Backend') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Backend') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BooleanOperands():
    """
    Object representingn boolean operands search criteria.

    :attr str bool_expression: (optional) Boolean search condition.
    :attr List[BoolOperand] bool_operands: (optional) Ontology artifacts supporing
          boolean search condition.
    """

    def __init__(self, *, bool_expression: str = None, bool_operands: List['BoolOperand'] = None) -> None:
        """
        Initialize a BooleanOperands object.

        :param str bool_expression: (optional) Boolean search condition.
        :param List[BoolOperand] bool_operands: (optional) Ontology artifacts
               supporing boolean search condition.
        """
        self.bool_expression = bool_expression
        self.bool_operands = bool_operands

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'BooleanOperands':
        """Initialize a BooleanOperands object from a json dictionary."""
        args = {}
        if 'boolExpression' in _dict:
            args['bool_expression'] = _dict.get('boolExpression')
        if 'boolOperands' in _dict:
            args['bool_operands'] = [BoolOperand.from_dict(x) for x in _dict.get('boolOperands')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BooleanOperands object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'bool_expression') and self.bool_expression is not None:
            _dict['boolExpression'] = self.bool_expression
        if hasattr(self, 'bool_operands') and self.bool_operands is not None:
            _dict['boolOperands'] = [x.to_dict() for x in self.bool_operands]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BooleanOperands object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'BooleanOperands') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'BooleanOperands') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BooleanConcepts(object):
    """
    Object representingn boolean concept search criteria.
    :attr str bool: (optional) Boolean search condition.
    :attr list[Concept] concepts: (optional) Ontology artifacts supporing boolean search
    condition.
    """

    def __init__(self, bool_term=None, concepts=None):
        """
        Initialize a BooleanConcepts object.
        :param str bool: (optional) Boolean search condition.
        :param list[Concept] concepts: (optional) Ontology artifacts supporing boolean
        search condition.
        """
        self.bool = bool_term
        self.concepts = concepts

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a BooleanConcepts object from a json dictionary."""
        args = {}
        if 'bool' in _dict:
            args['bool'] = _dict.get('bool')
        if 'concepts' in _dict:
            args['concepts'] = [Concept._from_dict(x) for x in _dict.get('concepts')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'bool') and self.bool is not None:
            _dict['bool'] = self.bool
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x._to_dict() for x in self.concepts]
        return _dict

    def __str__(self):
        """Return a `str` version of this BooleanConcepts object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BoolOperand():
    """
    BoolOperand.

    :attr str bool_operand: (optional)
    """

    def __init__(self, *, bool_operand: str = None) -> None:
        """
        Initialize a BoolOperand object.

        :param str bool_operand: (optional)
        """
        self.bool_operand = bool_operand

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'BoolOperand':
        """Initialize a BoolOperand object from a json dictionary."""
        args = {}
        if 'boolOperand' in _dict:
            args['bool_operand'] = _dict.get('boolOperand')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BoolOperand object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'bool_operand') and self.bool_operand is not None:
            _dict['boolOperand'] = self.bool_operand
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BoolOperand object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'BoolOperand') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'BoolOperand') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CategoriesModel():
    """
    Model representing ontology categories.

    :attr str model_license: (optional) License for corpus.
    :attr str highlighted_title: (optional)
    :attr str highlighted_abstract: (optional)
    :attr str highlighted_body: (optional)
    :attr dict highlighted_sections: (optional) Document sections with annotation
          tags.
    :attr dict passages: (optional) Document passages with annotation tags.
    :attr dict annotations: (optional) List of document annotations.
    """

    def __init__(self, *, model_license: str = None, highlighted_title: 'StringBuilder' = None, highlighted_abstract: 'StringBuilder' = None, highlighted_body: 'StringBuilder' = None, highlighted_sections: dict = None, passages: dict = None, annotations: dict = None) -> None:
        """
        Initialize a CategoriesModel object.

        :param str model_license: (optional) License for corpus.
        :param str highlighted_title: (optional)
        :param str highlighted_abstract: (optional)
        :param str highlighted_body: (optional)
        :param dict highlighted_sections: (optional) Document sections with
               annotation tags.
        :param dict passages: (optional) Document passages with annotation tags.
        :param dict annotations: (optional) List of document annotations.
        """
        self.model_license = model_license
        self.highlighted_title = highlighted_title
        self.highlighted_abstract = highlighted_abstract
        self.highlighted_body = highlighted_body
        self.highlighted_sections = highlighted_sections
        self.passages = passages
        self.annotations = annotations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CategoriesModel':
        """Initialize a CategoriesModel object from a json dictionary."""
        args = {}
        if 'modelLicense' in _dict:
            args['model_license'] = _dict.get('modelLicense')
        if 'highlightedTitle' in _dict:
            args['highlighted_title'] = _dict.get('highlightedTitle')
        if 'highlightedAbstract' in _dict:
            args['highlighted_abstract'] = _dict.get('highlightedAbstract')
        if 'highlightedBody' in _dict:
            args['highlighted_body'] = _dict.get('highlightedBody')
        if 'highlightedSections' in _dict:
            args['highlighted_sections'] = {k : StringBuilder.from_dict(v) for k,v in _dict.get('highlightedSections').items()}
        if 'passages' in _dict:
            args['passages'] = _dict.get('passages')
        if 'annotations' in _dict:
            args['annotations'] = {k : AnnotationModel.from_dict(v) for k,v in _dict.get('annotations').items()}
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CategoriesModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'model_license') and self.model_license is not None:
            _dict['modelLicense'] = self.model_license
        if hasattr(self, 'highlighted_title') and self.highlighted_title is not None:
            _dict['highlightedTitle'] = self.highlighted_title
        if hasattr(self, 'highlighted_abstract') and self.highlighted_abstract is not None:
            _dict['highlightedAbstract'] = self.highlighted_abstract
        if hasattr(self, 'highlighted_body') and self.highlighted_body is not None:
            _dict['highlightedBody'] = self.highlighted_body
        if hasattr(self, 'highlighted_sections') and self.highlighted_sections is not None:
            _dict['highlightedSections'] = {k : v.to_dict() for k,v in self.highlighted_sections.items()}
        if hasattr(self, 'passages') and self.passages is not None:
            _dict['passages'] = self.passages
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = {k : v.to_dict() for k,v in self.annotations.items()}
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CategoriesModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CategoriesModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CategoriesModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Category(object):
    """
    Category.
    :attr str name: (optional)
    :attr list[str] types: (optional)
    :attr str category: (optional)
    :attr bool only_negated_concepts: (optional)
    """

    def __init__(self, name=None, types=None, category=None, only_negated_concepts=None):
        """
        Initialize a Category object.
        :param str name: (optional)
        :param list[str] types: (optional)
        :param str category: (optional)
        :param bool only_negated_concepts: (optional)
        """
        self.name = name
        self.types = types
        self.category = category
        self.only_negated_concepts = only_negated_concepts

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Category object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'types' in _dict:
            args['types'] = _dict.get('types')
        if 'category' in _dict:
            args['category'] = _dict.get('category')
        if 'onlyNegatedConcepts' in _dict:
            args['only_negated_concepts'] = _dict.get('onlyNegatedConcepts')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types
        if hasattr(self, 'category') and self.category is not None:
            _dict['category'] = self.category
        if hasattr(self, 'only_negated_concepts') and self.only_negated_concepts is not None:
            _dict['onlyNegatedConcepts'] = self.only_negated_concepts
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Category object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CommonDataModel():
    """
    Model representing common data across annotations.

    :attr List[UnstructuredModel] unstructured: (optional) Object of all ontology
          artifacts found in the document.
    """

    def __init__(self, *, unstructured: List['UnstructuredModel'] = None) -> None:
        """
        Initialize a CommonDataModel object.

        :param List[UnstructuredModel] unstructured: (optional) Object of all
               ontology artifacts found in the document.
        """
        self.unstructured = unstructured

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CommonDataModel':
        """Initialize a CommonDataModel object from a json dictionary."""
        args = {}
        if 'unstructured' in _dict:
            args['unstructured'] = [UnstructuredModel.from_dict(x) for x in _dict.get('unstructured')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CommonDataModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unstructured') and self.unstructured is not None:
            _dict['unstructured'] = [x.to_dict() for x in self.unstructured]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CommonDataModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CommonDataModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CommonDataModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Concept():
    """
    Object reprensting an ontology artifact.

    :attr str ontology: (optional) Ontology for artifact in search results.
    :attr str cui: (optional) Unique identifier for ontolgoy artifact in search
          results.
    :attr str preferred_name: (optional) Ontology defined semantic type for artifact
          in search results.
    :attr str alternative_name: (optional) Ontology defined normalized name for
          artifact in search results.
    :attr str semantic_type: (optional) Ontology defined alternative name for
          artifact in search results.
    :attr int count: (optional) Corpus frequency of artifact.
    :attr int hit_count: (optional) Corpus frequency of artifact.
    :attr float score: (optional) Relevancy score of artifact in search results.
    :attr Count parents: (optional) Corpus frequency count.
    :attr Count children: (optional) Corpus frequency count.
    :attr Count siblings: (optional) Corpus frequency count.
    :attr Count related: (optional) Corpus frequency count.
    :attr List[str] document_ids: (optional) Document identifiers for artifacts in
          search results.
    :attr str data_type: (optional) attribute data type for artifact in search
          results.
    :attr str unit: (optional) Attribute value unit for artifact.
    :attr str operator: (optional) Attribute value operator for artifact.
    :attr str min_value: (optional) Minimum value for attribute artifact.
    :attr str max_value: (optional) Maximum value for attribute artifact.
    :attr str vocab: (optional) Source vocabulary of arttifact.
    :attr List[str] properties: (optional) Artifact properties.
    """

    def __init__(self, *, ontology: str = None, cui: str = None, preferred_name: str = None, alternative_name: str = None, semantic_type: str = None, count: int = None, hit_count: int = None, score: float = None, parents: 'Count' = None, children: 'Count' = None, siblings: 'Count' = None, related: 'Count' = None, document_ids: List[str] = None, data_type: str = None, unit: str = None, operator: str = None, min_value: str = None, max_value: str = None, vocab: str = None, properties: List[str] = None) -> None:
        """
        Initialize a Concept object.

        :param str ontology: (optional) Ontology for artifact in search results.
        :param str cui: (optional) Unique identifier for ontolgoy artifact in
               search results.
        :param str preferred_name: (optional) Ontology defined semantic type for
               artifact in search results.
        :param str alternative_name: (optional) Ontology defined normalized name
               for artifact in search results.
        :param str semantic_type: (optional) Ontology defined alternative name for
               artifact in search results.
        :param int count: (optional) Corpus frequency of artifact.
        :param int hit_count: (optional) Corpus frequency of artifact.
        :param float score: (optional) Relevancy score of artifact in search
               results.
        :param Count parents: (optional) Corpus frequency count.
        :param Count children: (optional) Corpus frequency count.
        :param Count siblings: (optional) Corpus frequency count.
        :param Count related: (optional) Corpus frequency count.
        :param List[str] document_ids: (optional) Document identifiers for
               artifacts in search results.
        :param str data_type: (optional) attribute data type for artifact in search
               results.
        :param str unit: (optional) Attribute value unit for artifact.
        :param str operator: (optional) Attribute value operator for artifact.
        :param str min_value: (optional) Minimum value for attribute artifact.
        :param str max_value: (optional) Maximum value for attribute artifact.
        :param str vocab: (optional) Source vocabulary of arttifact.
        :param List[str] properties: (optional) Artifact properties.
        """
        self.ontology = ontology
        self.cui = cui
        self.preferred_name = preferred_name
        self.alternative_name = alternative_name
        self.semantic_type = semantic_type
        self.count = count
        self.hit_count = hit_count
        self.score = score
        self.parents = parents
        self.children = children
        self.siblings = siblings
        self.related = related
        self.document_ids = document_ids
        self.data_type = data_type
        self.unit = unit
        self.operator = operator
        self.min_value = min_value
        self.max_value = max_value
        self.vocab = vocab
        self.properties = properties

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Concept':
        """Initialize a Concept object from a json dictionary."""
        args = {}
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'alternativeName' in _dict:
            args['alternative_name'] = _dict.get('alternativeName')
        if 'semanticType' in _dict:
            args['semantic_type'] = _dict.get('semanticType')
        if 'count' in _dict:
            args['count'] = _dict.get('count')
        if 'hitCount' in _dict:
            args['hit_count'] = _dict.get('hitCount')
        if 'score' in _dict:
            args['score'] = _dict.get('score')
        if 'parents' in _dict:
            args['parents'] = Count.from_dict(_dict.get('parents'))
        if 'children' in _dict:
            args['children'] = Count.from_dict(_dict.get('children'))
        if 'siblings' in _dict:
            args['siblings'] = Count.from_dict(_dict.get('siblings'))
        if 'related' in _dict:
            args['related'] = Count.from_dict(_dict.get('related'))
        if 'documentIds' in _dict:
            args['document_ids'] = _dict.get('documentIds')
        if 'dataType' in _dict:
            args['data_type'] = _dict.get('dataType')
        if 'unit' in _dict:
            args['unit'] = _dict.get('unit')
        if 'operator' in _dict:
            args['operator'] = _dict.get('operator')
        if 'minValue' in _dict:
            args['min_value'] = _dict.get('minValue')
        if 'maxValue' in _dict:
            args['max_value'] = _dict.get('maxValue')
        if 'vocab' in _dict:
            args['vocab'] = _dict.get('vocab')
        if 'properties' in _dict:
            args['properties'] = _dict.get('properties')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Concept object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'alternative_name') and self.alternative_name is not None:
            _dict['alternativeName'] = self.alternative_name
        if hasattr(self, 'semantic_type') and self.semantic_type is not None:
            _dict['semanticType'] = self.semantic_type
        if hasattr(self, 'count') and self.count is not None:
            _dict['count'] = self.count
        if hasattr(self, 'hit_count') and self.hit_count is not None:
            _dict['hitCount'] = self.hit_count
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'parents') and self.parents is not None:
            _dict['parents'] = self.parents.to_dict()
        if hasattr(self, 'children') and self.children is not None:
            _dict['children'] = self.children.to_dict()
        if hasattr(self, 'siblings') and self.siblings is not None:
            _dict['siblings'] = self.siblings.to_dict()
        if hasattr(self, 'related') and self.related is not None:
            _dict['related'] = self.related.to_dict()
        if hasattr(self, 'document_ids') and self.document_ids is not None:
            _dict['documentIds'] = self.document_ids
        if hasattr(self, 'data_type') and self.data_type is not None:
            _dict['dataType'] = self.data_type
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'operator') and self.operator is not None:
            _dict['operator'] = self.operator
        if hasattr(self, 'min_value') and self.min_value is not None:
            _dict['minValue'] = self.min_value
        if hasattr(self, 'max_value') and self.max_value is not None:
            _dict['maxValue'] = self.max_value
        if hasattr(self, 'vocab') and self.vocab is not None:
            _dict['vocab'] = self.vocab
        if hasattr(self, 'properties') and self.properties is not None:
            _dict['properties'] = self.properties
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Concept object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Concept') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Concept') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ConceptInfoModel():
    """
    Model representing ontology annotations.

    :attr str cui: (optional) Ontology provided unique identifier for artifact.
    :attr str ontology: (optional) Source onology of artifact.
    :attr str preferred_name: (optional) Ontology defined normalized name for
          artifact.
    :attr List[str] semantic_types: (optional) Ontology defined semanic types for
          artifact.
    :attr List[str] surface_forms: (optional) Ontology defined synonyms for
          artifact.
    :attr str definition: (optional) Ontology provided definition for artifact.
    :attr bool has_parents: (optional) Whether the artifact has parent artifacts in
          the ontology.
    :attr bool has_children: (optional) Whether the artifact has child artifacts in
          the ontology.
    :attr bool has_siblings: (optional) Whether the artifact has sibling artifacts
          in the ontology.
    """

    def __init__(self, *, cui: str = None, ontology: str = None, preferred_name: str = None, semantic_types: List[str] = None, surface_forms: List[str] = None, definition: str = None, has_parents: bool = None, has_children: bool = None, has_siblings: bool = None) -> None:
        """
        Initialize a ConceptInfoModel object.

        :param str cui: (optional) Ontology provided unique identifier for
               artifact.
        :param str ontology: (optional) Source onology of artifact.
        :param str preferred_name: (optional) Ontology defined normalized name for
               artifact.
        :param List[str] semantic_types: (optional) Ontology defined semanic types
               for artifact.
        :param List[str] surface_forms: (optional) Ontology defined synonyms for
               artifact.
        :param str definition: (optional) Ontology provided definition for
               artifact.
        :param bool has_parents: (optional) Whether the artifact has parent
               artifacts in the ontology.
        :param bool has_children: (optional) Whether the artifact has child
               artifacts in the ontology.
        :param bool has_siblings: (optional) Whether the artifact has sibling
               artifacts in the ontology.
        """
        self.cui = cui
        self.ontology = ontology
        self.preferred_name = preferred_name
        self.semantic_types = semantic_types
        self.surface_forms = surface_forms
        self.definition = definition
        self.has_parents = has_parents
        self.has_children = has_children
        self.has_siblings = has_siblings

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ConceptInfoModel':
        """Initialize a ConceptInfoModel object from a json dictionary."""
        args = {}
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'semanticTypes' in _dict:
            args['semantic_types'] = _dict.get('semanticTypes')
        if 'surfaceForms' in _dict:
            args['surface_forms'] = _dict.get('surfaceForms')
        if 'definition' in _dict:
            args['definition'] = _dict.get('definition')
        if 'hasParents' in _dict:
            args['has_parents'] = _dict.get('hasParents')
        if 'hasChildren' in _dict:
            args['has_children'] = _dict.get('hasChildren')
        if 'hasSiblings' in _dict:
            args['has_siblings'] = _dict.get('hasSiblings')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ConceptInfoModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'semantic_types') and self.semantic_types is not None:
            _dict['semanticTypes'] = self.semantic_types
        if hasattr(self, 'surface_forms') and self.surface_forms is not None:
            _dict['surfaceForms'] = self.surface_forms
        if hasattr(self, 'definition') and self.definition is not None:
            _dict['definition'] = self.definition
        if hasattr(self, 'has_parents') and self.has_parents is not None:
            _dict['hasParents'] = self.has_parents
        if hasattr(self, 'has_children') and self.has_children is not None:
            _dict['hasChildren'] = self.has_children
        if hasattr(self, 'has_siblings') and self.has_siblings is not None:
            _dict['hasSiblings'] = self.has_siblings
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ConceptInfoModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ConceptInfoModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ConceptInfoModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ConceptListModel():
    """
    List of ontolgoy artifacts.

    :attr List[Concept] concepts: (optional) List of ontology artifacts.
    """

    def __init__(self, *, concepts: List['Concept'] = None) -> None:
        """
        Initialize a ConceptListModel object.

        :param List[Concept] concepts: (optional) List of ontology artifacts.
        """
        self.concepts = concepts

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ConceptListModel':
        """Initialize a ConceptListModel object from a json dictionary."""
        args = {}
        if 'concepts' in _dict:
            args['concepts'] = [Concept.from_dict(x) for x in _dict.get('concepts')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ConceptListModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x.to_dict() for x in self.concepts]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ConceptListModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ConceptListModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ConceptListModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ConceptModel():
    """
    Model representing an ontology annotation.

    :attr int unique_id: (optional) Service generated unique identifier of ontology
          artifact.
    :attr List[int] sticky_ids: (optional) Identifiers associated with artifact
          unique identifier.
    :attr str section: (optional) Document section where artifact was found.
    :attr str type: (optional) Ontology semantic type for artifact (if applicable).
    :attr int begin: (optional) Staring offset of artifact in document section.
    :attr int end: (optional) Ending offset of artifact in document section.
    :attr str covered_text: (optional) Actual document section text artifact
          represents.
    :attr str cui: (optional) Ontology defined unique identifier of artifact.
    :attr str preferred_name: (optional) Ontology defined normalized name of
          artifact.
    :attr str source: (optional) Ontology providing the artifact.
    :attr bool negated: (optional) Whether span represented by artifact is negated.
    :attr bool hypothetical: (optional) Whether span represented by artifact is
          hypothetical.
    :attr int timestamp: (optional) Time based offset of artifact in a video
          transcript (if applicable).
    :attr str attribute_id: (optional) Identifier of attribute where artifact is
          defined (if applicable).
    :attr List[str] qualifiers: (optional) List of qualifers defined for an
          attribute artifact.
    :attr str unit: (optional) Unit of measure for attribute defined artifact (if
          applicable).
    :attr str min_value: (optional) Starting range value for attribute artifact (if
          applicable).
    :attr str max_value: (optional) Ending range value for attribute artifact (if
          applicable).
    :attr str operator: (optional) Mathmatical operator for attribute artifact (if
          applicable).
    :attr dict features: (optional) List of additional artifact features.
    :attr str nlu_entity_index: (optional) Model coreference chain to which artifact
          belongs.
    :attr str nlu_mention_index: (optional) Artifact position in Model coreference
          chain.
    :attr str nlu_relation_id: (optional) Relation unique identifier artifact is
          associated with.
    :attr str nlu_side: (optional) Whether artifact is a source or target of a
          relationship.
    :attr str nlu_source_type: (optional) Model type for artifact when the source of
          a relationship.
    :attr str nlu_relation: (optional) Name of the realtion an artifact is
          associated with.
    :attr str nlu_target_type: (optional) Model type for artifact when the target of
          a relationship.
    :attr int hits: (optional) Number of times artifact is mentioned in the corpus.
    """

    def __init__(self, *, unique_id: int = None, sticky_ids: List[int] = None, section: str = None, type: str = None, begin: int = None, end: int = None, covered_text: str = None, cui: str = None, preferred_name: str = None, source: str = None, negated: bool = None, hypothetical: bool = None, timestamp: int = None, attribute_id: str = None, qualifiers: List[str] = None, unit: str = None, min_value: str = None, max_value: str = None, operator: str = None, features: dict = None, nlu_entity_index: str = None, nlu_mention_index: str = None, nlu_relation_id: str = None, nlu_side: str = None, nlu_source_type: str = None, nlu_relation: str = None, nlu_target_type: str = None, hits: int = None) -> None:
        """
        Initialize a ConceptModel object.

        :param int unique_id: (optional) Service generated unique identifier of
               ontology artifact.
        :param List[int] sticky_ids: (optional) Identifiers associated with
               artifact unique identifier.
        :param str section: (optional) Document section where artifact was found.
        :param str type: (optional) Ontology semantic type for artifact (if
               applicable).
        :param int begin: (optional) Staring offset of artifact in document
               section.
        :param int end: (optional) Ending offset of artifact in document section.
        :param str covered_text: (optional) Actual document section text artifact
               represents.
        :param str cui: (optional) Ontology defined unique identifier of artifact.
        :param str preferred_name: (optional) Ontology defined normalized name of
               artifact.
        :param str source: (optional) Ontology providing the artifact.
        :param bool negated: (optional) Whether span represented by artifact is
               negated.
        :param bool hypothetical: (optional) Whether span represented by artifact
               is hypothetical.
        :param int timestamp: (optional) Time based offset of artifact in a video
               transcript (if applicable).
        :param str attribute_id: (optional) Identifier of attribute where artifact
               is defined (if applicable).
        :param List[str] qualifiers: (optional) List of qualifers defined for an
               attribute artifact.
        :param str unit: (optional) Unit of measure for attribute defined artifact
               (if applicable).
        :param str min_value: (optional) Starting range value for attribute
               artifact (if applicable).
        :param str max_value: (optional) Ending range value for attribute artifact
               (if applicable).
        :param str operator: (optional) Mathmatical operator for attribute artifact
               (if applicable).
        :param dict features: (optional) List of additional artifact features.
        :param str nlu_entity_index: (optional) Model coreference chain to which
               artifact belongs.
        :param str nlu_mention_index: (optional) Artifact position in Model
               coreference chain.
        :param str nlu_relation_id: (optional) Relation unique identifier artifact
               is associated with.
        :param str nlu_side: (optional) Whether artifact is a source or target of a
               relationship.
        :param str nlu_source_type: (optional) Model type for artifact when the
               source of a relationship.
        :param str nlu_relation: (optional) Name of the realtion an artifact is
               associated with.
        :param str nlu_target_type: (optional) Model type for artifact when the
               target of a relationship.
        :param int hits: (optional) Number of times artifact is mentioned in the
               corpus.
        """
        self.unique_id = unique_id
        self.sticky_ids = sticky_ids
        self.section = section
        self.type = type
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.cui = cui
        self.preferred_name = preferred_name
        self.source = source
        self.negated = negated
        self.hypothetical = hypothetical
        self.timestamp = timestamp
        self.attribute_id = attribute_id
        self.qualifiers = qualifiers
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.operator = operator
        self.features = features
        self.nlu_entity_index = nlu_entity_index
        self.nlu_mention_index = nlu_mention_index
        self.nlu_relation_id = nlu_relation_id
        self.nlu_side = nlu_side
        self.nlu_source_type = nlu_source_type
        self.nlu_relation = nlu_relation
        self.nlu_target_type = nlu_target_type
        self.hits = hits

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ConceptModel':
        """Initialize a ConceptModel object from a json dictionary."""
        args = {}
        if 'uniqueId' in _dict:
            args['unique_id'] = _dict.get('uniqueId')
        if 'stickyIds' in _dict:
            args['sticky_ids'] = _dict.get('stickyIds')
        if 'section' in _dict:
            args['section'] = _dict.get('section')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'begin' in _dict:
            args['begin'] = _dict.get('begin')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        if 'coveredText' in _dict:
            args['covered_text'] = _dict.get('coveredText')
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'source' in _dict:
            args['source'] = _dict.get('source')
        if 'negated' in _dict:
            args['negated'] = _dict.get('negated')
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict.get('hypothetical')
        if 'timestamp' in _dict:
            args['timestamp'] = _dict.get('timestamp')
        if 'attributeId' in _dict:
            args['attribute_id'] = _dict.get('attributeId')
        if 'qualifiers' in _dict:
            args['qualifiers'] = _dict.get('qualifiers')
        if 'unit' in _dict:
            args['unit'] = _dict.get('unit')
        if 'minValue' in _dict:
            args['min_value'] = _dict.get('minValue')
        if 'maxValue' in _dict:
            args['max_value'] = _dict.get('maxValue')
        if 'operator' in _dict:
            args['operator'] = _dict.get('operator')
        if 'features' in _dict:
            args['features'] = _dict.get('features')
        if 'nluEntityIndex' in _dict:
            args['nlu_entity_index'] = _dict.get('nluEntityIndex')
        if 'nluMentionIndex' in _dict:
            args['nlu_mention_index'] = _dict.get('nluMentionIndex')
        if 'nluRelationId' in _dict:
            args['nlu_relation_id'] = _dict.get('nluRelationId')
        if 'nluSide' in _dict:
            args['nlu_side'] = _dict.get('nluSide')
        if 'nluSourceType' in _dict:
            args['nlu_source_type'] = _dict.get('nluSourceType')
        if 'nluRelation' in _dict:
            args['nlu_relation'] = _dict.get('nluRelation')
        if 'nluTargetType' in _dict:
            args['nlu_target_type'] = _dict.get('nluTargetType')
        if 'hits' in _dict:
            args['hits'] = _dict.get('hits')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ConceptModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unique_id') and self.unique_id is not None:
            _dict['uniqueId'] = self.unique_id
        if hasattr(self, 'sticky_ids') and self.sticky_ids is not None:
            _dict['stickyIds'] = self.sticky_ids
        if hasattr(self, 'section') and self.section is not None:
            _dict['section'] = self.section
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = self.timestamp
        if hasattr(self, 'attribute_id') and self.attribute_id is not None:
            _dict['attributeId'] = self.attribute_id
        if hasattr(self, 'qualifiers') and self.qualifiers is not None:
            _dict['qualifiers'] = self.qualifiers
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'min_value') and self.min_value is not None:
            _dict['minValue'] = self.min_value
        if hasattr(self, 'max_value') and self.max_value is not None:
            _dict['maxValue'] = self.max_value
        if hasattr(self, 'operator') and self.operator is not None:
            _dict['operator'] = self.operator
        if hasattr(self, 'features') and self.features is not None:
            _dict['features'] = self.features
        if hasattr(self, 'nlu_entity_index') and self.nlu_entity_index is not None:
            _dict['nluEntityIndex'] = self.nlu_entity_index
        if hasattr(self, 'nlu_mention_index') and self.nlu_mention_index is not None:
            _dict['nluMentionIndex'] = self.nlu_mention_index
        if hasattr(self, 'nlu_relation_id') and self.nlu_relation_id is not None:
            _dict['nluRelationId'] = self.nlu_relation_id
        if hasattr(self, 'nlu_side') and self.nlu_side is not None:
            _dict['nluSide'] = self.nlu_side
        if hasattr(self, 'nlu_source_type') and self.nlu_source_type is not None:
            _dict['nluSourceType'] = self.nlu_source_type
        if hasattr(self, 'nlu_relation') and self.nlu_relation is not None:
            _dict['nluRelation'] = self.nlu_relation
        if hasattr(self, 'nlu_target_type') and self.nlu_target_type is not None:
            _dict['nluTargetType'] = self.nlu_target_type
        if hasattr(self, 'hits') and self.hits is not None:
            _dict['hits'] = self.hits
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ConceptModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ConceptModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ConceptModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Concepts(object):
    """
    Concepts.
    :attr str ontology: (optional)
    :attr int limit: (optional)
    :attr str scope: (optional)
    :attr list[str] types: (optional)
    :attr str mode: (optional)
    """

    def __init__(self, ontology=None, limit=None, scope=None, types=None, mode=None):
        """
        Initialize a Concepts object.
        :param str ontology: (optional)
        :param int limit: (optional)
        :param str scope: (optional)
        :param list[str] types: (optional)
        :param str mode: (optional)
        """
        self.ontology = ontology
        self.limit = limit
        self.scope = scope
        self.types = types
        self.mode = mode

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Concepts object from a json dictionary."""
        args = {}
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'scope' in _dict:
            args['scope'] = _dict.get('scope')
        if 'types' in _dict:
            args['types'] = _dict.get('types')
        if 'mode' in _dict:
            args['mode'] = _dict.get('mode')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'scope') and self.scope is not None:
            _dict['scope'] = self.scope
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types
        if hasattr(self, 'mode') and self.mode is not None:
            _dict['mode'] = self.mode
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Concepts object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CorporaConfigModel():
    """
    Model respresenting configured corpora.

    :attr List[CorpusModel] corpora: (optional) List of corpora found in the
          instance.
    """

    def __init__(self, *, corpora: List['CorpusModel'] = None) -> None:
        """
        Initialize a CorporaConfig object.

        :param List[CorpusModel] corpora: (optional) List of corpora found in the
               instance.
        """
        self.corpora = corpora

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CorporaConfig':
        """Initialize a CorporaConfig object from a json dictionary."""
        args = {}
        if 'corpora' in _dict:
            args['corpora'] = [CorpusModel.from_dict(x) for x in _dict.get('corpora')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CorporaConfig object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'corpora') and self.corpora is not None:
            _dict['corpora'] = [x.to_dict() for x in self.corpora]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CorporaConfig object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CorporaConfig') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CorporaConfig') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CorpusModel():
    """
    Object representing a configured corpus.

    :attr str corpus_name: (optional) Name of the corpus.
    :attr List[str] ontologies: (optional) Ontologies found in the corpus.
    :attr str descriptive_name: (optional) Descriptive name of the corpus.
    :attr bool bvt: (optional) BVT status of the corpus.
    :attr str elasticsearch_index: (optional) Repository location of the corpus.
    """

    def __init__(self, *, corpus_name: str = None, ontologies: List[str] = None, descriptive_name: str = None, bvt: bool = None, elasticsearch_index: str = None) -> None:
        """
        Initialize a CorpusModel object.

        :param str corpus_name: (optional) Name of the corpus.
        :param List[str] ontologies: (optional) Ontologies found in the corpus.
        :param str descriptive_name: (optional) Descriptive name of the corpus.
        :param bool bvt: (optional) BVT status of the corpus.
        :param str elasticsearch_index: (optional) Repository location of the
               corpus.
        """
        self.corpus_name = corpus_name
        self.ontologies = ontologies
        self.descriptive_name = descriptive_name
        self.bvt = bvt
        self.elasticsearch_index = elasticsearch_index

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CorpusModel':
        """Initialize a CorpusModel object from a json dictionary."""
        args = {}
        if 'corpusName' in _dict:
            args['corpus_name'] = _dict.get('corpusName')
        if 'ontologies' in _dict:
            args['ontologies'] = _dict.get('ontologies')
        if 'descriptiveName' in _dict:
            args['descriptive_name'] = _dict.get('descriptiveName')
        if 'bvt' in _dict:
            args['bvt'] = _dict.get('bvt')
        if 'elasticsearchIndex' in _dict:
            args['elasticsearch_index'] = _dict.get('elasticsearchIndex')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CorpusModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'corpus_name') and self.corpus_name is not None:
            _dict['corpusName'] = self.corpus_name
        if hasattr(self, 'ontologies') and self.ontologies is not None:
            _dict['ontologies'] = self.ontologies
        if hasattr(self, 'descriptive_name') and self.descriptive_name is not None:
            _dict['descriptiveName'] = self.descriptive_name
        if hasattr(self, 'bvt') and self.bvt is not None:
            _dict['bvt'] = self.bvt
        if hasattr(self, 'elasticsearch_index') and self.elasticsearch_index is not None:
            _dict['elasticsearchIndex'] = self.elasticsearch_index
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CorpusModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CorpusModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CorpusModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CorpusInfoModel(object):
    """
    CorpusInfoModel.
    :attr int document_count: (optional)
    :attr list[CorpusProvider] providers: (optional)
    """

    def __init__(self, document_count=None, providers=None):
        """
        Initialize a CorpusInfoModel object.
        :param int document_count: (optional)
        :param list[CorpusProvider] providers: (optional)
        """
        self.document_count = document_count
        self.providers = providers

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a CorpusInfoModel object from a json dictionary."""
        args = {}
        if 'documentCount' in _dict:
            args['document_count'] = _dict.get('documentCount')
        if 'providers' in _dict:
            args['providers'] = [CorpusProvider._from_dict(x) for x in _dict.get('providers')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'document_count') and self.document_count is not None:
            _dict['documentCount'] = self.document_count
        if hasattr(self, 'providers') and self.providers is not None:
            _dict['providers'] = [x._to_dict() for x in self.providers]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this CorpusInfoModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class CorpusProvider(object):
    """
    CorpusProvider.
    :attr int document_count: (optional)
    :attr str name: (optional)
    """

    def __init__(self, document_count=None, name=None):
        """
        Initialize a CorpusProvider object.
        :param int document_count: (optional)
        :param str name: (optional)
        """
        self.document_count = document_count
        self.name = name

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a CorpusProvider object from a json dictionary."""
        args = {}
        if 'documentCount' in _dict:
            args['document_count'] = _dict.get('documentCount')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'document_count') and self.document_count is not None:
            _dict['documentCount'] = self.document_count
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this CorpusProvider object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Count():
    """
    Corpus frequency count.

    :attr int count: (optional) Number of documents for artifact result.
    :attr int hits: (optional) Number of documents for artifact result.
    """

    def __init__(self, *, count: int = None, hits: int = None) -> None:
        """
        Initialize a Count object.

        :param int count: (optional) Number of documents for artifact result.
        :param int hits: (optional) Number of documents for artifact result.
        """
        self.count = count
        self.hits = hits

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Count':
        """Initialize a Count object from a json dictionary."""
        args = {}
        if 'count' in _dict:
            args['count'] = _dict.get('count')
        if 'hits' in _dict:
            args['hits'] = _dict.get('hits')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Count object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'count') and self.count is not None:
            _dict['count'] = self.count
        if hasattr(self, 'hits') and self.hits is not None:
            _dict['hits'] = self.hits
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Count object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Count') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Count') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataModel():
    """
    Model representing ontology artifacts.

    :attr List[ConceptModel] concepts: (optional) List of ontolgy artifacts found in
          the document.
    :attr List[ConceptModel] attribute_values: (optional) List of ontolgy attribute
          value artifacts found in the document.
    :attr List[RelationModel] relations: (optional) List of ontology relations found
          in the document.
    :attr List[ConceptModel] mesh: (optional)
    :attr List[ConceptModel] text: (optional)
    """

    def __init__(self, *, concepts: List['ConceptModel'] = None, attribute_values: List['ConceptModel'] = None, relations: List['RelationModel'] = None, mesh: List['ConceptModel'] = None, text: List['ConceptModel'] = None) -> None:
        """
        Initialize a DataModel object.

        :param List[ConceptModel] concepts: (optional) List of ontolgy artifacts
               found in the document.
        :param List[ConceptModel] attribute_values: (optional) List of ontolgy
               attribute value artifacts found in the document.
        :param List[RelationModel] relations: (optional) List of ontology relations
               found in the document.
        :param List[ConceptModel] mesh: (optional)
        :param List[ConceptModel] text: (optional)
        """
        self.concepts = concepts
        self.attribute_values = attribute_values
        self.relations = relations
        self.mesh = mesh
        self.text = text

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataModel':
        """Initialize a DataModel object from a json dictionary."""
        args = {}
        if 'concepts' in _dict:
            args['concepts'] = [ConceptModel.from_dict(x) for x in _dict.get('concepts')]
        if 'attributeValues' in _dict:
            args['attribute_values'] = [ConceptModel.from_dict(x) for x in _dict.get('attributeValues')]
        if 'relations' in _dict:
            args['relations'] = [RelationModel.from_dict(x) for x in _dict.get('relations')]
        if 'mesh' in _dict:
            args['mesh'] = [ConceptModel.from_dict(x) for x in _dict.get('mesh')]
        if 'text' in _dict:
            args['text'] = [ConceptModel.from_dict(x) for x in _dict.get('text')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x.to_dict() for x in self.concepts]
        if hasattr(self, 'attribute_values') and self.attribute_values is not None:
            _dict['attributeValues'] = [x.to_dict() for x in self.attribute_values]
        if hasattr(self, 'relations') and self.relations is not None:
            _dict['relations'] = [x.to_dict() for x in self.relations]
        if hasattr(self, 'mesh') and self.mesh is not None:
            _dict['mesh'] = [x.to_dict() for x in self.mesh]
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = [x.to_dict() for x in self.text]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other



class DateHistograms(object):
    """
    DateHistograms.
    :attr str interval: (optional)
    :attr int utc: (optional)
    """

    def __init__(self, interval=None, utc=None):
        """
        Initialize a DateHistograms object.
        :param str interval: (optional)
        :param int utc: (optional)
        """
        self.interval = interval
        self.utc = utc

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a DateHistograms object from a json dictionary."""
        args = {}
        if 'interval' in _dict:
            args['interval'] = _dict.get('interval')
        if 'utc' in _dict:
            args['utc'] = _dict.get('utc')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'interval') and self.interval is not None:
            _dict['interval'] = self.interval
        if hasattr(self, 'utc') and self.utc is not None:
            _dict['utc'] = self.utc
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this DateHistograms object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DictionaryEntry():
    """
    DictionaryEntry.

    :attr List[str] children: (optional)
    :attr str cui: (optional)
    :attr List[str] definition: (optional)
    :attr List[str] parents: (optional)
    :attr str preferred_name: (optional)
    :attr List[str] semtypes: (optional)
    :attr List[str] siblings: (optional)
    :attr List[str] surface_forms: (optional)
    :attr List[str] variants: (optional)
    :attr str vocab: (optional)
    :attr List[str] related: (optional)
    :attr str source: (optional)
    :attr str source_version: (optional)
    """

    def __init__(self, *, children: List[str] = None, cui: str = None, definition: List[str] = None, parents: List[str] = None, preferred_name: str = None, semtypes: List[str] = None, siblings: List[str] = None, surface_forms: List[str] = None, variants: List[str] = None, vocab: str = None, related: List[str] = None, source: str = None, source_version: str = None) -> None:
        """
        Initialize a DictionaryEntry object.

        :param List[str] children: (optional)
        :param str cui: (optional)
        :param List[str] definition: (optional)
        :param List[str] parents: (optional)
        :param str preferred_name: (optional)
        :param List[str] semtypes: (optional)
        :param List[str] siblings: (optional)
        :param List[str] surface_forms: (optional)
        :param List[str] variants: (optional)
        :param str vocab: (optional)
        :param List[str] related: (optional)
        :param str source: (optional)
        :param str source_version: (optional)
        """
        self.children = children
        self.cui = cui
        self.definition = definition
        self.parents = parents
        self.preferred_name = preferred_name
        self.semtypes = semtypes
        self.siblings = siblings
        self.surface_forms = surface_forms
        self.variants = variants
        self.vocab = vocab
        self.related = related
        self.source = source
        self.source_version = source_version

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DictionaryEntry':
        """Initialize a DictionaryEntry object from a json dictionary."""
        args = {}
        if 'children' in _dict:
            args['children'] = _dict.get('children')
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'definition' in _dict:
            args['definition'] = _dict.get('definition')
        if 'parents' in _dict:
            args['parents'] = _dict.get('parents')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'semtypes' in _dict:
            args['semtypes'] = _dict.get('semtypes')
        if 'siblings' in _dict:
            args['siblings'] = _dict.get('siblings')
        if 'surfaceForms' in _dict:
            args['surface_forms'] = _dict.get('surfaceForms')
        if 'variants' in _dict:
            args['variants'] = _dict.get('variants')
        if 'vocab' in _dict:
            args['vocab'] = _dict.get('vocab')
        if 'related' in _dict:
            args['related'] = _dict.get('related')
        if 'source' in _dict:
            args['source'] = _dict.get('source')
        if 'source_version' in _dict:
            args['source_version'] = _dict.get('source_version')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DictionaryEntry object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'children') and self.children is not None:
            _dict['children'] = self.children
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'definition') and self.definition is not None:
            _dict['definition'] = self.definition
        if hasattr(self, 'parents') and self.parents is not None:
            _dict['parents'] = self.parents
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'semtypes') and self.semtypes is not None:
            _dict['semtypes'] = self.semtypes
        if hasattr(self, 'siblings') and self.siblings is not None:
            _dict['siblings'] = self.siblings
        if hasattr(self, 'surface_forms') and self.surface_forms is not None:
            _dict['surfaceForms'] = self.surface_forms
        if hasattr(self, 'variants') and self.variants is not None:
            _dict['variants'] = self.variants
        if hasattr(self, 'vocab') and self.vocab is not None:
            _dict['vocab'] = self.vocab
        if hasattr(self, 'related') and self.related is not None:
            _dict['related'] = self.related
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'source_version') and self.source_version is not None:
            _dict['source_version'] = self.source_version
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DictionaryEntry object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DictionaryEntry') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DictoinaryEntry') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Documents(object):
    """
    Documents.
    :attr int limit: (optional)
    :attr int offset: (optional)
    :attr dict metadata: (optional)
    :attr Passages passages: (optional)
    :attr list[SortEntry] sort: (optional)
    """

    def __init__(self, limit=None, offset=None, metadata=None, passages=None, sort=None):
        """
        Initialize a Documents object.
        :param int limit: (optional)
        :param int offset: (optional)
        :param dict metadata: (optional)
        :param Passages passages: (optional)
        :param list[SortEntry] sort: (optional)
        """
        self.limit = limit
        self.offset = offset
        self.metadata = metadata
        self.passages = passages
        self.sort = sort

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Documents object from a json dictionary."""
        args = {}
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'offset' in _dict:
            args['offset'] = _dict.get('offset')
        if 'metadata' in _dict:
            args['metadata'] = _dict.get('metadata')
        if 'passages' in _dict:
            args['passages'] = _dict.get('passages')
        if 'sort' in _dict:
            args['sort'] = [SortEntry._from_dict(x) for x in _dict.get('sort')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'offset') and self.offset is not None:
            _dict['offset'] = self.offset
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        if hasattr(self, 'passages') and self.passages is not None:
            _dict['passages'] = self.passages
        if hasattr(self, 'sort') and self.sort is not None:
            _dict['sort'] = [x._to_dict() for x in self.sort]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Documents object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class EntryModel():
    """
    Object representing a passage.

    :attr str id: (optional) Unique identifier of passage.
    :attr bool negated: (optional) Whether passage is a negated span.
    :attr List[SentenceModel] sentences: (optional) List of sentences within
          passage.
    """

    def __init__(self, *, id: str = None, negated: bool = None, sentences: List['SentenceModel'] = None) -> None:
        """
        Initialize a EntryModel object.

        :param str id: (optional) Unique identifier of passage.
        :param bool negated: (optional) Whether passage is a negated span.
        :param List[SentenceModel] sentences: (optional) List of sentences within
               passage.
        """
        self.id = id
        self.negated = negated
        self.sentences = sentences

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'EntryModel':
        """Initialize a EntryModel object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'negated' in _dict:
            args['negated'] = _dict.get('negated')
        if 'sentences' in _dict:
            args['sentences'] = [SentenceModel.from_dict(x) for x in _dict.get('sentences')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a EntryModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'sentences') and self.sentences is not None:
            _dict['sentences'] = [x.to_dict() for x in self.sentences]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this EntryModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'EntryModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'EntryModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class FieldOptions():
    """
    Supported options for the field.

    :attr Supports supports: (optional) List of supported options.
    """

    def __init__(self, *, supports: dict = None) -> None:
        """
        Initialize a FieldOptions object.

        :param Supports supports: (optional) List of supported options.
        """
        self.supports = supports

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FieldOptions':
        """Initialize a FieldOptions object from a json dictionary."""
        args = {}
        if 'supports' in _dict:
            args['supports'] = Supports._from_dict(_dict.get('supports'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FieldOptions object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'supports') and self.supports is not None:
            _dict['supports'] = self.supports.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FieldOptions object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'FieldOptions') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FieldOptions') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class GetDocumentInfoResponse():
    """
    GetDocumentInfoResponse.

    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize a GetDocumentInfoResponse object.

        :param **kwargs: (optional) Any additional properties.
        """
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetDocumentInfoResponse':
        """Initialize a GetDocumentInfoResponse object from a json dictionary."""
        return cls(**_dict)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetDocumentInfoResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        return vars(self)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetDocumentInfoResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetDocumentInfoResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetDocumentInfoResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class HistogramData():
    """
    histogram data.

    :attr str date: (optional) Date associated with result.
    :attr int hits: (optional) Number of documents for date range result.
    """

    def __init__(self, *, date: str = None, hits: int = None) -> None:
        """
        Initialize a HistogramData object.

        :param str date: (optional) Date associated with result.
        :param int hits: (optional) Number of documents for date range result.
        """
        self.date = date
        self.hits = hits

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'HistogramData':
        """Initialize a HistogramData object from a json dictionary."""
        args = {}
        if 'date' in _dict:
            args['date'] = _dict.get('date')
        if 'hits' in _dict:
            args['hits'] = _dict.get('hits')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a HistogramData object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'date') and self.date is not None:
            _dict['date'] = self.date
        if hasattr(self, 'hits') and self.hits is not None:
            _dict['hits'] = self.hits
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this HistogramData object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'HistogramData') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'HistogramData') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class HitCount():
    """
    Corpus frequency of artifact.

    :attr int hit_count: (optional) Corpus frequency of artifact.
    """

    def __init__(self, *, hit_count: int = None) -> None:
        """
        Initialize a HitCount object.

        :param int hit_count: (optional) Corpus frequency of artifact.
        """
        self.hit_count = hit_count

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'HitCount':
        """Initialize a HitCount object from a json dictionary."""
        args = {}
        if 'hitCount' in _dict:
            args['hit_count'] = _dict.get('hitCount')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a HitCount object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'hit_count') and self.hit_count is not None:
            _dict['hitCount'] = self.hit_count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this HitCount object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'HitCount') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'HitCount') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Message():
    """
    Object representing repository message.

    :attr str message_type: (optional) Message semantic type.
    :attr str url: (optional) Message link.
    :attr object request: (optional) Message request.
    :attr List[str] headers: (optional) Request headers.
    :attr int status: (optional) Message status.
    :attr object response: (optional) Message response.
    """

    def __init__(self, *, message_type: str = None, url: str = None, request: object = None, headers: List[str] = None, status: int = None, response: object = None) -> None:
        """
        Initialize a Message object.

        :param str message_type: (optional) Message semantic type.
        :param str url: (optional) Message link.
        :param object request: (optional) Message request.
        :param List[str] headers: (optional) Request headers.
        :param int status: (optional) Message status.
        :param object response: (optional) Message response.
        """
        self.message_type = message_type
        self.url = url
        self.request = request
        self.headers = headers
        self.status = status
        self.response = response

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Message':
        """Initialize a Message object from a json dictionary."""
        args = {}
        if 'messageType' in _dict:
            args['message_type'] = _dict.get('messageType')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'request' in _dict:
            args['request'] = _dict.get('request')
        if 'headers' in _dict:
            args['headers'] = _dict.get('headers')
        if 'status' in _dict:
            args['status'] = _dict.get('status')
        if 'response' in _dict:
            args['response'] = _dict.get('response')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Message object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'message_type') and self.message_type is not None:
            _dict['messageType'] = self.message_type
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'request') and self.request is not None:
            _dict['request'] = self.request
        if hasattr(self, 'headers') and self.headers is not None:
            _dict['headers'] = self.headers
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status
        if hasattr(self, 'response') and self.response is not None:
            _dict['response'] = self.response
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Message object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Message') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Message') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    
    class MessageTypeEnum(Enum):
        """
        Message semantic type.
        """
        EXPANDED_REQUEST = "expanded_request"
        ELASTIC_SEARCH = "elastic_search"


class MetadataFields():
    """
    MetadataFields.

    :attr str corpus: (optional) Corpus name.
    :attr str corpus_description: (optional) Corpus description.
    :attr dict fields: (optional) Metadata fields.
    """

    def __init__(self, *, corpus: str = None, corpus_description: str = None, fields: dict = None) -> None:
        """
        Initialize a MetadataFields object.

        :param str corpus: (optional) Corpus name.
        :param str corpus_description: (optional) Corpus description.
        :param dict fields: (optional) Metadata fields.
        """
        self.corpus = corpus
        self.corpus_description = corpus_description
        self.fields = fields

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetadataFields':
        """Initialize a MetadataFields object from a json dictionary."""
        args = {}
        if 'corpus' in _dict:
            args['corpus'] = _dict.get('corpus')
        if 'corpusDescription' in _dict:
            args['corpus_description'] = _dict.get('corpusDescription')
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetadataFields object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'corpus') and self.corpus is not None:
            _dict['corpus'] = self.corpus
        if hasattr(self, 'corpus_description') and self.corpus_description is not None:
            _dict['corpusDescription'] = self.corpus_description
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = self.fields
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetadataFields object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetadataFields') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetadataFields') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class MetadataModel():
    """
    Model for document metadata.

    :attr dict fields: (optional) List of document fields in the corpus.
    :attr List[str] section_field_names: (optional) List of fields that where
          enriched.
    :attr List[str] attr_section_field_names: (optional) List of fields enriched
          with attributes.
    :attr List[str] qualifier_section_field_names: (optional) List of fields
          enriched with attribute qualifiers.
    :attr List[str] mesh_section_field_names: (optional) List of fields with MeSH
          annotations.
    :attr dict field_index_map: (optional)
    """

    def __init__(self, *, fields: dict = None, section_field_names: List[str] = None, attr_section_field_names: List[str] = None, qualifier_section_field_names: List[str] = None, mesh_section_field_names: List[str] = None, field_index_map: dict = None) -> None:
        """
        Initialize a MetadataModel object.

        :param dict fields: (optional) List of document fields in the corpus.
        :param List[str] section_field_names: (optional) List of fields that where
               enriched.
        :param List[str] attr_section_field_names: (optional) List of fields
               enriched with attributes.
        :param List[str] qualifier_section_field_names: (optional) List of fields
               enriched with attribute qualifiers.
        :param List[str] mesh_section_field_names: (optional) List of fields with
               MeSH annotations.
        :param dict field_index_map: (optional)
        """
        self.fields = fields
        self.section_field_names = section_field_names
        self.attr_section_field_names = attr_section_field_names
        self.qualifier_section_field_names = qualifier_section_field_names
        self.mesh_section_field_names = mesh_section_field_names
        self.field_index_map = field_index_map

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetadataModel':
        """Initialize a MetadataModel object from a json dictionary."""
        args = {}
        if 'fields' in _dict:
            args['fields'] = {k : FieldOptions.from_dict(v) for k,v in _dict.get('fields').items()}
        if 'sectionFieldNames' in _dict:
            args['section_field_names'] = _dict.get('sectionFieldNames')
        if 'attrSectionFieldNames' in _dict:
            args['attr_section_field_names'] = _dict.get('attrSectionFieldNames')
        if 'qualifierSectionFieldNames' in _dict:
            args['qualifier_section_field_names'] = _dict.get('qualifierSectionFieldNames')
        if 'meshSectionFieldNames' in _dict:
            args['mesh_section_field_names'] = _dict.get('meshSectionFieldNames')
        if 'fieldIndexMap' in _dict:
            args['field_index_map'] = _dict.get('fieldIndexMap')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetadataModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = {k : v.to_dict() for k,v in self.fields.items()}
        if hasattr(self, 'section_field_names') and self.section_field_names is not None:
            _dict['sectionFieldNames'] = self.section_field_names
        if hasattr(self, 'attr_section_field_names') and self.attr_section_field_names is not None:
            _dict['attrSectionFieldNames'] = self.attr_section_field_names
        if hasattr(self, 'qualifier_section_field_names') and self.qualifier_section_field_names is not None:
            _dict['qualifierSectionFieldNames'] = self.qualifier_section_field_names
        if hasattr(self, 'mesh_section_field_names') and self.mesh_section_field_names is not None:
            _dict['meshSectionFieldNames'] = self.mesh_section_field_names
        if hasattr(self, 'field_index_map') and self.field_index_map is not None:
            _dict['fieldIndexMap'] = self.field_index_map
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetadataModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetadataModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetadataModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Order(object):
    """
    Object representing sort order preference.
    :attr str order: sort direction
    """

    def __init__(self, order):
        """
        Initialize a SortEntry object.
        :param str order: sort direction
        """
        self.order = order

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ServiceStatus object from a json dictionary."""
        args = {}
        if 'order' in _dict:
            args['order'] = _dict.get('order')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'order') and self.order is not None:
            _dict['order'] = self.order
        return _dict

    def __str__(self):
        """Return a `str` version of this ServiceStatus object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Passage():
    """
    Object representing a document passage.

    :attr str document_section: (optional) Document section for passage.
    :attr StringBuilder text: (optional)
    :attr int timestamp: (optional) Timestamp of passage in video transcript.
    :attr str preferred_name: (optional) Preferred name for highlighted text span.
    """

    def __init__(self, *, document_section: str = None, text: 'StringBuilder' = None, timestamp: int = None, preferred_name: str = None) -> None:
        """
        Initialize a Passage object.

        :param str document_section: (optional) Document section for passage.
        :param StringBuilder text: (optional)
        :param int timestamp: (optional) Timestamp of passage in video transcript.
        :param str preferred_name: (optional) Preferred name for highlighted text
               span.
        """
        self.document_section = document_section
        self.text = text
        self.timestamp = timestamp
        self.preferred_name = preferred_name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Passage':
        """Initialize a Passage object from a json dictionary."""
        args = {}
        if 'documentSection' in _dict:
            args['document_section'] = _dict.get('documentSection')
        if 'text' in _dict:
            args['text'] = StringBuilder.from_dict(_dict.get('text'))
        if 'timestamp' in _dict:
            args['timestamp'] = _dict.get('timestamp')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Passage object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'document_section') and self.document_section is not None:
            _dict['documentSection'] = self.document_section
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text.to_dict()
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = self.timestamp
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Passage object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Passage') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Passage') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Passages(object):
    """
    Passages.
    :attr list[Concept] concepts_to_highlight: (regquired)
    :attr str search_tag_begin: (optional)
    :attr str search_tag_end: (optional)
    :attr str related_tag_begin: (optional)
    :attr str related_tag_end: (optional)
    :attr int limit: (optional)
    :attr float min_score: (optional)
    """

    def __init__(self, concepts_to_highlight=None, search_tag_begin=None, search_tag_end=None,
                 related_tag_begin=None, related_tag_end=None, limit=None, min_score=None):
        """
        Initialize a Passages object.
        :attr list[Concept] concepts_to_highlight: (required)
        :param str search_tag_begin: (optional)
        :param str search_tag_end: (optional)
        :param str related_tag_begin: (optional)
        :param str related_tag_end: (optional)
        :param int limit: (optional)
        :param float min_score: (optional)
        """
        self.concepts_to_highlight = concepts_to_highlight
        self.search_tag_begin = search_tag_begin
        self.search_tag_end = search_tag_end
        self.related_tag_begin = related_tag_begin
        self.related_tag_end = related_tag_end
        self.limit = limit
        self.min_score = min_score

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Passages object from a json dictionary."""
        args = {}
        if 'conceptsToHighlight' in _dict:
            args['concepts_to_highlight'] = ([Concept._from_dict(x) for x in
                                              _dict.get('conceptsToHighlight')])
        if 'searchTagBegin' in _dict:
            args['search_tag_begin'] = _dict.get('searchTagBegin')
        if 'searchTagEnd' in _dict:
            args['search_tag_end'] = _dict.get('searchTagEnd')
        if 'relatedTagBegin' in _dict:
            args['related_tag_begin'] = _dict.get('relatedTagBegin')
        if 'relatedTagEnd' in _dict:
            args['related_tag_end'] = _dict.get('relatedTagEnd')
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'minScore' in _dict:
            args['min_score'] = _dict.get('minScore')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'concepts_to_highlight') and self.concepts_to_highlight is not None:
            _dict['conceptsToHighlight'] = [x._to_dict() for x in self.concepts_to_highlight]
        if hasattr(self, 'search_tag_begin') and self.search_tag_begin is not None:
            _dict['searchTagBegin'] = self.search_tag_begin
        if hasattr(self, 'search_tag_end') and self.search_tag_end is not None:
            _dict['searchTagEnd'] = self.search_tag_end
        if hasattr(self, 'related_tag_begin') and self.related_tag_begin is not None:
            _dict['relatedTagBegin'] = self.related_tag_begin
        if hasattr(self, 'related_tag_end') and self.related_tag_end is not None:
            _dict['relatedTagEnd'] = self.related_tag_end
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'min_score') and self.min_score is not None:
            _dict['minScore'] = self.min_score
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Passages object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class PassagesModel():
    """
    PassagesModel.

    :attr List[Passage] all_passages: (optional) Document passages.
    :attr dict search_term_to_passages: (optional) Search term to passages.
    """

    def __init__(self, *, all_passages: List['Passage'] = None, search_term_to_passages: dict = None) -> None:
        """
        Initialize a PassagesModel object.

        :param List[Passage] all_passages: (optional) Document passages.
        :param dict search_term_to_passages: (optional) Search term to passages.
        """
        self.all_passages = all_passages
        self.search_term_to_passages = search_term_to_passages

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PassagesModel':
        """Initialize a PassagesModel object from a json dictionary."""
        args = {}
        if 'allPassages' in _dict:
            args['all_passages'] = [Passage.from_dict(x) for x in _dict.get('allPassages')]
        if 'searchTermToPassages' in _dict:
            args['search_term_to_passages'] = _dict.get('searchTermToPassages')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PassagesModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'all_passages') and self.all_passages is not None:
            _dict['allPassages'] = [x.to_dict() for x in self.all_passages]
        if hasattr(self, 'search_term_to_passages') and self.search_term_to_passages is not None:
            _dict['searchTermToPassages'] = self.search_term_to_passages
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PassagesModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PassagesModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PassagesModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class PossibleValues():
    """
    PossibleValues.

    :attr str display_value: (optional)
    :attr str value: (optional)
    """

    def __init__(self, *, display_value: str = None, value: str = None) -> None:
        """
        Initialize a PossbileValues object.

        :param str display_value: (optional)
        :param str value: (optional)
        """
        self.display_value = display_value
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PossbileValues':
        """Initialize a PossbileValues object from a json dictionary."""
        args = {}
        if 'displayValue' in _dict:
            args['display_value'] = _dict.get('displayValue')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PossbileValues object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'display_value') and self.display_value is not None:
            _dict['displayValue'] = self.display_value
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PossbileValues object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PossbileValues') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PossbileValues') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Qualifier():
    """
    Object representing an artifact qualifier.

    :attr str id: (optional) Unique identifier for attribute qualifier.
    :attr str name: (optional) Name of attribute qualifier.
    """

    def __init__(self, *, id: str = None, name: str = None) -> None:
        """
        Initialize a Qualifer object.

        :param str id: (optional) Unique identifier for attribute qualifier.
        :param str name: (optional) Name of attribute qualifier.
        """
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Qualifer':
        """Initialize a Qualifer object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Qualifer object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Qualifer object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Qualifer') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Qualifer') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Query(object):
    """
    Query.
    :attr str boolExpression: (optional)
    :attr list[SearchableConcept] concepts: (optional)
    :attr dict boolTerm: (optional)
    :attr dict boolRegexp: (optional)
    :attr list[dict] regexp: (optional)
    :attr dict date_range: (optional)
    :attr Title title: (optional)
    :attr str cursorId: (optional)
    :attr list[dict] operands: (optional)
    :attr bool rankedSearch: (optional)
    """

    def __init__(self, boolExpression=None, concepts=None, boolTerm=None, boolRegexp=None, regexp=None,
                 date_range=None, title=None, operands=None, cursorId=None, rankedSearch=True):
        """
        Initialize a Query object.
        :param str boolExpression: (optional)
        :param list[SearchableConcept] concepts: (optional)
        :param dict boolTerm: (optional)
        :param dict boolRegexp: (optional)
        :param list[dict] regexp: (optional)
        :param dict date_range: (optional)
        :param Title title: (optional)
        :param str cursorId: (optional)
        :param list[dict] operands: (optional)
        :param bool rankedSearch: (optional)
        """
        self.boolExpression = boolExpression
        self.concepts = concepts
        self.boolTerm = boolTerm
        self.boolRegexp = boolRegexp
        self.regexp = regexp
        self.date_range = date_range
        self.title = title
        self.cursorId = cursorId
        self.operands = operands
        self.rankedSearch = rankedSearch

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Query object from a json dictionary."""
        args = {}
        if 'boolExpression' in _dict:
            args['boolExpression'] = _dict.get('boolExpression')
        if 'concepts' in _dict:
            args['concepts'] = _dict.get('concepts')
        if 'booTterm' in _dict:
            args['boolTerm'] = _dict.get('boolTerm')
        if 'boolRegexp' in _dict:
            args['boolRegexp'] = _dict.get('boolRegexp')
        if 'regexp' in _dict:
            args['regexp'] = _dict.get('regexp')
        if 'date_range' in _dict:
            args['date_range'] = {k : Range._from_dict(v) for k, v in _dict.get('date_range')}
        if 'title' in _dict:
            args['title'] = Title._from_dict(_dict.get('title'))
        if 'cursorId' in _dict:
            args['cursorId'] = _dict.get('cursorId')
        if 'operands' in _dict:
            args['operands'] = _dict.get('operands')
        if 'rankedSearch' in _dict:
            args['rankedSearch'] = _dict.get('rankedSearch')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'boolExpression') and self.boolExpression is not None:
            _dict['boolExpression'] = self.boolExpression
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = self.concepts
        if hasattr(self, 'boolTerm') and self.boolTerm is not None:
            _dict['boolTerm'] = self.boolTerm
        if hasattr(self, 'boolRegexp') and self.boolRegexp is not None:
            _dict['boolRegexp'] = self.boolRegexp
        if hasattr(self, 'regexp') and self.regexp is not None:
            _dict['regexp'] = self.regexp
        if hasattr(self, 'date_range') and self.date_range is not None:
            _dict['dateRange'] = self.date_range
        if hasattr(self, 'title') and self.title is not None:
            _dict['title'] = self.title._to_dict()
        if hasattr(self, 'cursorId') and self.cursorId is not None:
            _dict['cursorId'] = self.cursorId
        if hasattr(self, 'operands') and self.operands is not None:
            _dict['operands'] = self.operands
        if hasattr(self, 'rankedSearch') and self.rankedSearch is not None:
            _dict['rankedSearch'] = self.rankedSearch
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Query object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Range(object):
    """
    Range.
    :attr str begin: (optional)
    :attr str end: (optional)
    """

    def __init__(self, begin=None, end=None):
        """
        Initialize a Range object.
        :param str begin: (optional)
        :param str end: (optional)
        """
        self.begin = begin
        self.end = end

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Range object from a json dictionary."""
        args = {}
        if 'begin' in _dict:
            args['begin'] = _dict.get('begin')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Range object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Ranges(object):
    """
    Ranges.
    :attr str attribute_id: (optional)
    """

    def __init__(self, attribute_id=None):
        """
        Initialize a Ranges object.
        :param str attribute_id: (optional)
        """
        self.attribute_id = attribute_id

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Ranges object from a json dictionary."""
        args = {}
        if 'attributeId' in _dict:
            args['attribute_id'] = _dict.get('attributeId')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'attribute_id') and self.attribute_id is not None:
            _dict['attributeId'] = self.attribute_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Ranges object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RangeModel():
    """
    Object representing an attribute value range.

    :attr str operator: (optional) Operator assigned to attribute value.
    :attr str min: (optional) Minimum value assigned to attribute value.
    :attr str max: (optional) Maximum value assigned to attribute value.
    :attr int count: (optional) Corpus frequency for attribute value.
    """

    def __init__(self, *, operator: str = None, min: str = None, max: str = None, count: int = None) -> None:
        """
        Initialize a RangeModel object.

        :param str operator: (optional) Operator assigned to attribute value.
        :param str min: (optional) Minimum value assigned to attribute value.
        :param str max: (optional) Maximum value assigned to attribute value.
        :param int count: (optional) Corpus frequency for attribute value.
        """
        self.operator = operator
        self.min = min
        self.max = max
        self.count = count

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RangeModel':
        """Initialize a RangeModel object from a json dictionary."""
        args = {}
        if 'operator' in _dict:
            args['operator'] = _dict.get('operator')
        if 'min' in _dict:
            args['min'] = _dict.get('min')
        if 'max' in _dict:
            args['max'] = _dict.get('max')
        if 'count' in _dict:
            args['count'] = _dict.get('count')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RangeModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'operator') and self.operator is not None:
            _dict['operator'] = self.operator
        if hasattr(self, 'min') and self.min is not None:
            _dict['min'] = self.min
        if hasattr(self, 'max') and self.max is not None:
            _dict['max'] = self.max
        if hasattr(self, 'count') and self.count is not None:
            _dict['count'] = self.count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RangeModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RangeModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RangeModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RankedDocLinks():
    """
    RankedDocLinks.

    :attr str href_search_matches: (optional) Links for search matches.
    :attr str href_categories: (optional) Links for categorized search matches.
    """

    def __init__(self, *, href_search_matches: str = None, href_categories: str = None) -> None:
        """
        Initialize a RankedDocLinks object.

        :param str href_search_matches: (optional) Links for search matches.
        :param str href_categories: (optional) Links for categorized search
               matches.
        """
        self.href_search_matches = href_search_matches
        self.href_categories = href_categories

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RankedDocLinks':
        """Initialize a RankedDocLinks object from a json dictionary."""
        args = {}
        if 'hrefSearchMatches' in _dict:
            args['href_search_matches'] = _dict.get('hrefSearchMatches')
        if 'hrefCategories' in _dict:
            args['href_categories'] = _dict.get('hrefCategories')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RankedDocLinks object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'href_search_matches') and self.href_search_matches is not None:
            _dict['hrefSearchMatches'] = self.href_search_matches
        if hasattr(self, 'href_categories') and self.href_categories is not None:
            _dict['hrefCategories'] = self.href_categories
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RankedDocLinks object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RankedDocLinks') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RankedDocLinks') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RankedDocument():
    """
    Object representing a document search result.

    :attr str document_id: (optional) Document identifier.
    :attr str title: (optional) Document title.
    :attr dict metadata: (optional) Additional document fields.
    :attr str section_name: (optional) Document section.
    :attr str section_id: (optional) Document section identifier.
    :attr str corpus: (optional) Document corpus.
    :attr RankedDocLinks links: (optional)
    :attr PassagesModel passages: (optional)
    :attr dict annotations: (optional) Document annotations.
    """

    def __init__(self, *, document_id: str = None, title: str = None, metadata: dict = None, section_name: str = None, section_id: str = None, corpus: str = None, links: 'RankedDocLinks' = None, passages: 'PassagesModel' = None, annotations: dict = None) -> None:
        """
        Initialize a RankedDocument object.

        :param str document_id: (optional) Document identifier.
        :param str title: (optional) Document title.
        :param dict metadata: (optional) Additional document fields.
        :param str section_name: (optional) Document section.
        :param str section_id: (optional) Document section identifier.
        :param str corpus: (optional) Document corpus.
        :param RankedDocLinks links: (optional)
        :param PassagesModel passages: (optional)
        :param dict annotations: (optional) Document annotations.
        """
        self.document_id = document_id
        self.title = title
        self.metadata = metadata
        self.section_name = section_name
        self.section_id = section_id
        self.corpus = corpus
        self.links = links
        self.passages = passages
        self.annotations = annotations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RankedDocument':
        """Initialize a RankedDocument object from a json dictionary."""
        args = {}
        if 'documentId' in _dict:
            args['document_id'] = _dict.get('documentId')
        if 'title' in _dict:
            args['title'] = _dict.get('title')
        if 'metadata' in _dict:
            args['metadata'] = _dict.get('metadata')
        if 'sectionName' in _dict:
            args['section_name'] = _dict.get('sectionName')
        if 'sectionId' in _dict:
            args['section_id'] = _dict.get('sectionId')
        if 'corpus' in _dict:
            args['corpus'] = _dict.get('corpus')
        if 'links' in _dict:
            args['links'] = RankedDocLinks.from_dict(_dict.get('links'))
        if 'passages' in _dict:
            args['passages'] = PassagesModel.from_dict(_dict.get('passages'))
        if 'annotations' in _dict:
            args['annotations'] = {k : AnnotationModel.from_dict(v) for k,v in _dict.get('annotations').items()}
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RankedDocument object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'document_id') and self.document_id is not None:
            _dict['documentId'] = self.document_id
        if hasattr(self, 'title') and self.title is not None:
            _dict['title'] = self.title
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        if hasattr(self, 'section_name') and self.section_name is not None:
            _dict['sectionName'] = self.section_name
        if hasattr(self, 'section_id') and self.section_id is not None:
            _dict['sectionId'] = self.section_id
        if hasattr(self, 'corpus') and self.corpus is not None:
            _dict['corpus'] = self.corpus
        if hasattr(self, 'links') and self.links is not None:
            _dict['links'] = self.links.to_dict()
        if hasattr(self, 'passages') and self.passages is not None:
            _dict['passages'] = self.passages.to_dict()
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = {k : v.to_dict() for k,v in self.annotations.items()}
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RankedDocument object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RankedDocument') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RankedDocument') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RelatedConceptModel():
    """
    Model for concept ontology relation.

    :attr str cui: (optional) Ontology provided unique identifier for artifact.
    :attr str ontology: (optional) Source ontology for artifact.
    :attr str preferred_name: (optional) Ontology provided normalized name for
          artifact.
    :attr str alternative_name: (optional) Ontology provided alternative name for
          artifact.
    :attr str semantic_type: (optional) Ontology semantic type for artifact.
    :attr int rank: (optional) Search weight assigned to artifact.
    :attr int hit_count: (optional) Number of corpus documents artifact was found
          in.
    :attr float score: (optional) Relevance score for artifact.
    :attr List[str] surface_forms: (optional) List of artifact synonyms.
    :attr List[RelatedConceptModel] next_concepts: (optional) List of artifacts for
          the relation.
    """

    def __init__(self, *, cui: str = None, ontology: str = None, preferred_name: str = None, alternative_name: str = None, semantic_type: str = None, rank: int = None, hit_count: int = None, score: float = None, surface_forms: List[str] = None, next_concepts: List['RelatedConceptModel'] = None) -> None:
        """
        Initialize a RelatedConceptModel object.

        :param str cui: (optional) Ontology provided unique identifier for
               artifact.
        :param str ontology: (optional) Source ontology for artifact.
        :param str preferred_name: (optional) Ontology provided normalized name for
               artifact.
        :param str alternative_name: (optional) Ontology provided alternative name
               for artifact.
        :param str semantic_type: (optional) Ontology semantic type for artifact.
        :param int rank: (optional) Search weight assigned to artifact.
        :param int hit_count: (optional) Number of corpus documents artifact was
               found in.
        :param float score: (optional) Relevance score for artifact.
        :param List[str] surface_forms: (optional) List of artifact synonyms.
        :param List[RelatedConceptModel] next_concepts: (optional) List of
               artifacts for the relation.
        """
        self.cui = cui
        self.ontology = ontology
        self.preferred_name = preferred_name
        self.alternative_name = alternative_name
        self.semantic_type = semantic_type
        self.rank = rank
        self.hit_count = hit_count
        self.score = score
        self.surface_forms = surface_forms
        self.next_concepts = next_concepts

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RelatedConceptModel':
        """Initialize a RelatedConceptModel object from a json dictionary."""
        args = {}
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict.get('preferredName')
        if 'alternativeName' in _dict:
            args['alternative_name'] = _dict.get('alternativeName')
        if 'semanticType' in _dict:
            args['semantic_type'] = _dict.get('semanticType')
        if 'rank' in _dict:
            args['rank'] = _dict.get('rank')
        if 'hitCount' in _dict:
            args['hit_count'] = _dict.get('hitCount')
        if 'score' in _dict:
            args['score'] = _dict.get('score')
        if 'surfaceForms' in _dict:
            args['surface_forms'] = _dict.get('surfaceForms')
        if 'nextConcepts' in _dict:
            args['next_concepts'] = [RelatedConceptModel.from_dict(x) for x in _dict.get('nextConcepts')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RelatedConceptModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'alternative_name') and self.alternative_name is not None:
            _dict['alternativeName'] = self.alternative_name
        if hasattr(self, 'semantic_type') and self.semantic_type is not None:
            _dict['semanticType'] = self.semantic_type
        if hasattr(self, 'rank') and self.rank is not None:
            _dict['rank'] = self.rank
        if hasattr(self, 'hit_count') and self.hit_count is not None:
            _dict['hitCount'] = self.hit_count
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'surface_forms') and self.surface_forms is not None:
            _dict['surfaceForms'] = self.surface_forms
        if hasattr(self, 'next_concepts') and self.next_concepts is not None:
            _dict['nextConcepts'] = [x.to_dict() for x in self.next_concepts]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RelatedConceptModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RelatedConceptModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RelatedConceptModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RelatedConceptsModel():
    """
    Model for concept ontology relations.

    :attr List[RelatedConceptModel] concepts: (optional) List of artifacts for the
          relation.
    """

    def __init__(self, *, concepts: List['RelatedConceptModel'] = None) -> None:
        """
        Initialize a RelatedConceptsModel object.

        :param List[RelatedConceptModel] concepts: (optional) List of artifacts for
               the relation.
        """
        self.concepts = concepts

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RelatedConceptsModel':
        """Initialize a RelatedConceptsModel object from a json dictionary."""
        args = {}
        if 'concepts' in _dict:
            args['concepts'] = [RelatedConceptModel.from_dict(x) for x in _dict.get('concepts')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RelatedConceptsModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x.to_dict() for x in self.concepts]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RelatedConceptsModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RelatedConceptsModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RelatedConceptsModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class RelationModel():
    """
    Object representing an ontology relation.

    :attr str relation_id: (optional) Relation unique identifier artifact is
          associated with.
    :attr str relation: (optional) Name of the realtion an artifact is associated
          with.
    :attr TextSpan source: (optional) Objeft representing a document text span.
    :attr TextSpan target: (optional) Objeft representing a document text span.
    """

    def __init__(self, *, relation_id: str = None, relation: str = None, source: 'TextSpan' = None, target: 'TextSpan' = None) -> None:
        """
        Initialize a RelationModel object.

        :param str relation_id: (optional) Relation unique identifier artifact is
               associated with.
        :param str relation: (optional) Name of the realtion an artifact is
               associated with.
        :param TextSpan source: (optional) Objeft representing a document text
               span.
        :param TextSpan target: (optional) Objeft representing a document text
               span.
        """
        self.relation_id = relation_id
        self.relation = relation
        self.source = source
        self.target = target

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RelationModel':
        """Initialize a RelationModel object from a json dictionary."""
        args = {}
        if 'relationId' in _dict:
            args['relation_id'] = _dict.get('relationId')
        if 'relation' in _dict:
            args['relation'] = _dict.get('relation')
        if 'source' in _dict:
            args['source'] = TextSpan.from_dict(_dict.get('source'))
        if 'target' in _dict:
            args['target'] = TextSpan.from_dict(_dict.get('target'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RelationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'relation_id') and self.relation_id is not None:
            _dict['relationId'] = self.relation_id
        if hasattr(self, 'relation') and self.relation is not None:
            _dict['relation'] = self.relation
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source.to_dict()
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RelationModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RelationModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RelationModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ReturnsModel(object):
    """
    ReturnsModel.
    :attr Documents documents: (optional)
    :attr Concepts concepts: (optional)
    :attr Passages passages: (optional)
    :attr Attributes attributes: (optional)
    :attr Values values: (optional)
    :attr Ranges ranges: (optional)
    :attr Types types: (optional)
    :attr Typeahead typeahead: (optional)
    :attr dict date_histograms: (optional)
    :attr dict aggregations: (optional)
    """

    def __init__(self, documents=None, concepts=None, passages=None, attributes=None, values=None,
                 ranges=None, types=None, typeahead=None, date_histograms=None, aggregations=None):
        """
        Initialize a ReturnsModel object.
        :param Documents documents: (optional)
        :param Concepts concepts: (optional)
        :param Passages passages: (optional)
        :param Attributes attributes: (optional)
        :param Values values: (optional)
        :param Ranges ranges: (optional)
        :param Types types: (optional)
        :param Typeahead typeahead: (optional)
        :param DateHistograms date_histograms: (optional)
        :param Aggregations aggregations: (optional)
        """
        self.documents = documents
        self.concepts = concepts
        self.passages = passages
        self.attributes = attributes
        self.values = values
        self.ranges = ranges
        self.types = types
        self.typeahead = typeahead
        self.date_histograms = date_histograms
        self.aggregations = aggregations

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ReturnsModel object from a json dictionary."""
        args = {}
        if 'documents' in _dict:
            args['documents'] = Documents._from_dict(_dict.get('documents'))
        if 'concepts' in _dict:
            args['concepts'] = Concepts._from_dict(_dict.get('concepts'))
        if 'passages' in _dict:
            args['passages'] = Passages._from_dict(_dict.get('passages'))
        if 'attributes' in _dict:
            args['attributes'] = Attributes._from_dict(_dict.get('attributes'))
        if 'values' in _dict:
            args['values'] = Values._from_dict(_dict.get('values'))
        if 'ranges' in _dict:
            args['ranges'] = Ranges._from_dict(_dict.get('ranges'))
        if 'types' in _dict:
            args['types'] = TypesModel._from_dict(_dict.get('types'))
        if 'typeahead' in _dict:
            args['typeahead'] = Typeahead._from_dict(_dict.get('typeahead'))
        if 'dateHistograms' in _dict:
            args['date_histograms'] = ({k : DateHistograms._from_dict(v) for k, v in
                                        _dict.get('dateHistograms')})
        if 'aggregations' in _dict:
            args['aggregations'] = ({k : Aggregations._from_dict(v) for k, v in
                                     _dict.get('aggregations')})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'documents') and self.documents is not None:
            _dict['documents'] = self.documents._to_dict()
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = self.concepts._to_dict()
        if hasattr(self, 'passages') and self.passages is not None:
            _dict['passages'] = self.passages._to_dict()
        if hasattr(self, 'attributes') and self.attributes is not None:
            _dict['attributes'] = self.attributes._to_dict()
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values._to_dict()
        if hasattr(self, 'ranges') and self.ranges is not None:
            _dict['ranges'] = self.ranges._to_dict()
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types._to_dict()
        if hasattr(self, 'typeahead') and self.typeahead is not None:
            _dict['typeahead'] = self.typeahead._to_dict()
        if hasattr(self, 'date_histograms') and self.date_histograms is not None:
            _dict['dateHistograms'] = self.date_histograms
        if hasattr(self, 'aggregations') and self.aggregations is not None:
            _dict['aggregations'] = self.aggregations
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this ReturnsModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class SearchableConcept(object):
    """
    SearchableConcept.
    :attr str boolOperand: (optional)
    :attr str cui: (optional)
    :attr str ontology: (optional)
    :attr str rank: (optional)
    :attr str semanticType: (optional)
    :attr boolean negated: (optional)
    :attr list[str] includeRelated: (optional)
    """

    def __init__(self, boolOperand=None, cui=None, ontology=None, rank=None,
                 semanticType=None, negated=None, includeRelated=None):
        """
        :attr str boolOperand: (optional)
        :attr str cui: (optional)
        :attr str ontology: (optional)
        :attr str rank: (optional)
        :attr str semanticType: (optional)
        :attr boolean negated: (optional)
        :attr list[str] includeRelated: (optional)
        """
        self.boolOperand = boolOperand
        self.cui = cui
        self.ontology = ontology
        self.rank = rank
        self.semanticType = semanticType
        self.negated = negated
        self.includeRelated = includeRelated

    @classmethod
    def from_dict(cls, _dict):
        args = {}
        if 'boolOperand' in _dict:
            args['boolOperand'] = _dict.get('boolOperand')
        if 'cui' in _dict:
            args['cui'] = _dict.get('cui')
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'rank' in _dict:
            args['rank'] = _dict.get('rank')
        if 'semanticType' in _dict:
            args['semanticType'] = _dict.get('semanticType')
        if 'negated' in _dict:
            args['negated'] = _dict.get('negated')
        if 'includeRelated' in _dict:
            args['includeRelated'] = _dict.get('includeRelated')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        _dict = {}
        if hasattr(self, 'boolOperand') and self.boolOperand is not None:
            _dict['boolOperand'] = self.boolOperand
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'rank') and self.rank is not None:
            _dict['rank'] = self.rank
        if hasattr(self, 'semanticType') and self.semanticType is not None:
            _dict['semanticType'] = self.semanticType
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'includeRelated') and self.includeRelated is not None:
            _dict['includeRelated'] = self.includeRelated
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
#        return json.dumps(self._to_dict(), cls=SearchableConceptEncoder, indent=2)
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other


class SearchableConceptEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class SearchMatchesModel():
    """
    Object representing a corpus search match.

    :attr str external_id: (optional) Unique identifier for matched document in
          corpus.
    :attr str document_id: (optional) Unique identifier for matched document in
          corpus.
    :attr str parent_document_id: (optional) Unique identifier for matched document
          parent in corpus.
    :attr str publication_name: (optional) Publication name for matched document in
          corpus.
    :attr str publication_date: (optional) Publication date for matched document in
          corpus.
    :attr str publication_url: (optional) Publication URL for matched document in
          corpus.
    :attr List[str] authors: (optional) Authors of matched document in corpus.
    :attr str title: (optional) Title of matched document in corpus.
    :attr str medline_license: (optional) Usage license for matched document in
          corpus.
    :attr str href_pub_med: (optional) Pubmed link for matched document in corpus.
    :attr str href_pmc: (optional)
    :attr str href_doi: (optional)
    :attr str pdf_url: (optional) Link to PDF for matched document in corpus.
    :attr str reference_url: (optional) Link to sourc origin for matched document in
          corpus.
    :attr StringBuilder highlighted_title: (optional)
    :attr StringBuilder highlighted_abstract: (optional)
    :attr StringBuilder highlighted_body: (optional)
    :attr dict highlighted_sections: (optional) Matched document sections with
          annotation tags.
    :attr dict passages: (optional) Matched document passages with annotation tags.
    :attr dict annotations: (optional) Matched document annotations.
    """

    def __init__(self, *, external_id: str = None, document_id: str = None, parent_document_id: str = None, publication_name: str = None, publication_date: str = None, publication_url: str = None, authors: List[str] = None, title: str = None, medline_license: str = None, href_pub_med: str = None, href_pmc: str = None, href_doi: str = None, pdf_url: str = None, reference_url: str = None, highlighted_title: str = None, highlighted_abstract: str = None, highlighted_body: str = None, highlighted_sections: dict = None, passages: dict = None, annotations: dict = None) -> None:
        """
        Initialize a SearchMatchesModel object.

        :param str external_id: (optional) Unique identifier for matched document
               in corpus.
        :param str document_id: (optional) Unique identifier for matched document
               in corpus.
        :param str parent_document_id: (optional) Unique identifier for matched
               document parent in corpus.
        :param str publication_name: (optional) Publication name for matched
               document in corpus.
        :param str publication_date: (optional) Publication date for matched
               document in corpus.
        :param str publication_url: (optional) Publication URL for matched document
               in corpus.
        :param List[str] authors: (optional) Authors of matched document in corpus.
        :param str title: (optional) Title of matched document in corpus.
        :param str medline_license: (optional) Usage license for matched document
               in corpus.
        :param str href_pub_med: (optional) Pubmed link for matched document in
               corpus.
        :param str href_pmc: (optional)
        :param str href_doi: (optional)
        :param str pdf_url: (optional) Link to PDF for matched document in corpus.
        :param str reference_url: (optional) Link to sourc origin for matched
               document in corpus.
        :param StringBuilder highlighted_title: (optional)
        :param StringBuilder highlighted_abstract: (optional)
        :param StringBuilder highlighted_body: (optional)
        :param dict highlighted_sections: (optional) Matched document sections with
               annotation tags.
        :param dict passages: (optional) Matched document passages with annotation
               tags.
        :param dict annotations: (optional) Matched document annotations.
        """
        self.external_id = external_id
        self.document_id = document_id
        self.parent_document_id = parent_document_id
        self.publication_name = publication_name
        self.publication_date = publication_date
        self.publication_url = publication_url
        self.authors = authors
        self.title = title
        self.medline_license = medline_license
        self.href_pub_med = href_pub_med
        self.href_pmc = href_pmc
        self.href_doi = href_doi
        self.pdf_url = pdf_url
        self.reference_url = reference_url
        self.highlighted_title = highlighted_title
        self.highlighted_abstract = highlighted_abstract
        self.highlighted_body = highlighted_body
        self.highlighted_sections = highlighted_sections
        self.passages = passages
        self.annotations = annotations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SearchMatchesModel':
        """Initialize a SearchMatchesModel object from a json dictionary."""
        args = {}
        if 'externalId' in _dict:
            args['external_id'] = _dict.get('externalId')
        if 'documentId' in _dict:
            args['document_id'] = _dict.get('documentId')
        if 'parentDocumentId' in _dict:
            args['parent_document_id'] = _dict.get('parentDocumentId')
        if 'publicationName' in _dict:
            args['publication_name'] = _dict.get('publicationName')
        if 'publicationDate' in _dict:
            args['publication_date'] = _dict.get('publicationDate')
        if 'publicationURL' in _dict:
            args['publication_url'] = _dict.get('publicationURL')
        if 'authors' in _dict:
            args['authors'] = _dict.get('authors')
        if 'title' in _dict:
            args['title'] = _dict.get('title')
        if 'medlineLicense' in _dict:
            args['medline_license'] = _dict.get('medlineLicense')
        if 'hrefPubMed' in _dict:
            args['href_pub_med'] = _dict.get('hrefPubMed')
        if 'hrefPmc' in _dict:
            args['href_pmc'] = _dict.get('hrefPmc')
        if 'hrefDoi' in _dict:
            args['href_doi'] = _dict.get('hrefDoi')
        if 'pdfUrl' in _dict:
            args['pdf_url'] = _dict.get('pdfUrl')
        if 'referenceUrl' in _dict:
            args['reference_url'] = _dict.get('referenceUrl')
        if 'highlightedTitle' in _dict:
            args['highlighted_title'] = _dict.get('highlightedTitle')
        if 'highlightedAbstract' in _dict:
            args['highlighted_abstract'] = _dict.get('highlightedAbstract')
        if 'highlightedBody' in _dict:
            args['highlighted_body'] = _dict.get('highlightedBody')
        if 'highlightedSections' in _dict:
            args['highlighted_sections'] = {k : StringBuilder.from_dict(v) for k,v in _dict.get('highlightedSections').items()}
        if 'passages' in _dict:
            args['passages'] = _dict.get('passages')
        if 'annotations' in _dict:
            args['annotations'] = {k : AnnotationModel.from_dict(v) for k,v in _dict.get('annotations').items()}
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SearchMatchesModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'external_id') and self.external_id is not None:
            _dict['externalId'] = self.external_id
        if hasattr(self, 'document_id') and self.document_id is not None:
            _dict['documentId'] = self.document_id
        if hasattr(self, 'parent_document_id') and self.parent_document_id is not None:
            _dict['parentDocumentId'] = self.parent_document_id
        if hasattr(self, 'publication_name') and self.publication_name is not None:
            _dict['publicationName'] = self.publication_name
        if hasattr(self, 'publication_date') and self.publication_date is not None:
            _dict['publicationDate'] = self.publication_date
        if hasattr(self, 'publication_url') and self.publication_url is not None:
            _dict['publicationURL'] = self.publication_url
        if hasattr(self, 'authors') and self.authors is not None:
            _dict['authors'] = self.authors
        if hasattr(self, 'title') and self.title is not None:
            _dict['title'] = self.title
        if hasattr(self, 'medline_license') and self.medline_license is not None:
            _dict['medlineLicense'] = self.medline_license
        if hasattr(self, 'href_pub_med') and self.href_pub_med is not None:
            _dict['hrefPubMed'] = self.href_pub_med
        if hasattr(self, 'href_pmc') and self.href_pmc is not None:
            _dict['hrefPmc'] = self.href_pmc
        if hasattr(self, 'href_doi') and self.href_doi is not None:
            _dict['hrefDoi'] = self.href_doi
        if hasattr(self, 'pdf_url') and self.pdf_url is not None:
            _dict['pdfUrl'] = self.pdf_url
        if hasattr(self, 'reference_url') and self.reference_url is not None:
            _dict['referenceUrl'] = self.reference_url
        if hasattr(self, 'highlighted_title') and self.highlighted_title is not None:
            _dict['highlightedTitle'] = self.highlighted_title
        if hasattr(self, 'highlighted_abstract') and self.highlighted_abstract is not None:
            _dict['highlightedAbstract'] = self.highlighted_abstract
        if hasattr(self, 'highlighted_body') and self.highlighted_body is not None:
            _dict['highlightedBody'] = self.highlighted_body
        if hasattr(self, 'highlighted_sections') and self.highlighted_sections is not None:
            _dict['highlightedSections'] = {k : v.to_dict() for k,v in self.highlighted_sections.items()}
        if hasattr(self, 'passages') and self.passages is not None:
            _dict['passages'] = self.passages
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = {k : v.to_dict() for k,v in self.annotations.items()}
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SearchMatchesModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SearchMatchesModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SearchMatchesModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class SearchModel():
    """
    Model for search criteria.

    :attr str href: (optional) Link.
    :attr int page_number: (optional) Page number.
    :attr int get_limit: (optional) Search result limit.
    :attr int total_document_count: (optional) Total number of search matches in the
          corpus.
    :attr List[Concept] concepts: (optional) Ontology artifact results from search.
    :attr List[str] types: (optional) Ontology semantic types.
    :attr List[Attribute] attributes: (optional) Attribute artifact results from
          search.
    :attr List[Concept] values: (optional) Attribute artifact value results from
          search.
    :attr dict ranges: (optional) Attribute value range results from search.
    :attr List[Concept] typeahead: (optional) Type-ahead suggestion results in
          search.
    :attr dict aggregations: (optional) Aggregate result targets in search.
    :attr dict date_histograms: (optional) Date range of results from search.
    :attr List[Qualifer] qualifiers: (optional) Attribute qualifier results from
          search.
    :attr Backend backend: (optional) Object representing repository response.
    :attr object expanded_query: (optional) Search expression that includes all
          levels of criteria expression.
    :attr BooleanOperands parsed_bool_expression: (optional) Object representingn
          boolean operands search criteria.
    :attr dict concepts_exist: (optional) Whether ontolgoy artifacts were provided
          in search conditions.
    :attr str cursor_id: (optional)
    :attr List[str] vocabs: (optional)
    :attr dict annotations: (optional) Annotations returned for the document.
    :attr MetadataFields metadata: (optional)
    :attr List[RankedDocument] documents: (optional) Documents returned from search.
    :attr List[SearchModel] sub_queries: (optional)
    """

    def __init__(self, *, href: str = None, page_number: int = None, get_limit: int = None, total_document_count: int = None, concepts: List['Concept'] = None, types: List[str] = None, attributes: List['Attribute'] = None, values: List['Concept'] = None, ranges: dict = None, typeahead: List['Concept'] = None, aggregations: dict = None, date_histograms: dict = None, qualifiers: List['Qualifer'] = None, backend: 'Backend' = None, expanded_query: object = None, parsed_bool_expression: 'BooleanOperands' = None, concepts_exist: dict = None, cursor_id: str = None, vocabs: List[str] = None, annotations: dict = None, metadata: 'MetadataFields' = None, documents: List['RankedDocument'] = None, sub_queries: List['SearchModel'] = None) -> None:
        """
        Initialize a SearchModel object.

        :param str href: (optional) Link.
        :param int page_number: (optional) Page number.
        :param int get_limit: (optional) Search result limit.
        :param int total_document_count: (optional) Total number of search matches
               in the corpus.
        :param List[Concept] concepts: (optional) Ontology artifact results from
               search.
        :param List[str] types: (optional) Ontology semantic types.
        :param List[Attribute] attributes: (optional) Attribute artifact results
               from search.
        :param List[Concept] values: (optional) Attribute artifact value results
               from search.
        :param dict ranges: (optional) Attribute value range results from search.
        :param List[Concept] typeahead: (optional) Type-ahead suggestion results in
               search.
        :param dict aggregations: (optional) Aggregate result targets in search.
        :param dict date_histograms: (optional) Date range of results from search.
        :param List[Qualifer] qualifiers: (optional) Attribute qualifier results
               from search.
        :param Backend backend: (optional) Object representing repository response.
        :param object expanded_query: (optional) Search expression that includes
               all levels of criteria expression.
        :param BooleanOperands parsed_bool_expression: (optional) Object
               representingn boolean operands search criteria.
        :param dict concepts_exist: (optional) Whether ontolgoy artifacts were
               provided in search conditions.
        :param str cursor_id: (optional)
        :param List[str] vocabs: (optional)
        :param dict annotations: (optional) Annotations returned for the document.
        :param MetadataFields metadata: (optional)
        :param List[RankedDocument] documents: (optional) Documents returned from
               search.
        :param List[SearchModel] sub_queries: (optional)
        """
        self.href = href
        self.page_number = page_number
        self.get_limit = get_limit
        self.total_document_count = total_document_count
        self.concepts = concepts
        self.types = types
        self.attributes = attributes
        self.values = values
        self.ranges = ranges
        self.typeahead = typeahead
        self.aggregations = aggregations
        self.date_histograms = date_histograms
        self.qualifiers = qualifiers
        self.backend = backend
        self.expanded_query = expanded_query
        self.parsed_bool_expression = parsed_bool_expression
        self.concepts_exist = concepts_exist
        self.cursor_id = cursor_id
        self.vocabs = vocabs
        self.annotations = annotations
        self.metadata = metadata
        self.documents = documents
        self.sub_queries = sub_queries

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SearchModel':
        """Initialize a SearchModel object from a json dictionary."""
        args = {}
        if 'href' in _dict:
            args['href'] = _dict.get('href')
        if 'pageNumber' in _dict:
            args['page_number'] = _dict.get('pageNumber')
        if 'get_limit' in _dict:
            args['get_limit'] = _dict.get('get_limit')
        if 'totalDocumentCount' in _dict:
            args['total_document_count'] = _dict.get('totalDocumentCount')
        if 'concepts' in _dict:
            args['concepts'] = [Concept.from_dict(x) for x in _dict.get('concepts')]
        if 'types' in _dict:
            args['types'] = _dict.get('types')
        if 'attributes' in _dict:
            args['attributes'] = [Attribute.from_dict(x) for x in _dict.get('attributes')]
        if 'values' in _dict:
            args['values'] = [Concept.from_dict(x) for x in _dict.get('values')]
        if 'ranges' in _dict:
            args['ranges'] = {k : RangeModel.from_dict(v) for k,v in _dict.get('ranges').items()}
        if 'typeahead' in _dict:
            args['typeahead'] = [Concept.from_dict(x) for x in _dict.get('typeahead')]
        if 'aggregations' in _dict:
            args['aggregations'] = _dict.get('aggregations')
        if 'dateHistograms' in _dict:
            args['date_histograms'] = _dict.get('dateHistograms')
        if 'qualifiers' in _dict:
            args['qualifiers'] = [Qualifier.from_dict(x) for x in _dict.get('qualifiers')]
        if 'backend' in _dict:
            args['backend'] = Backend.from_dict(_dict.get('backend'))
        if 'expandedQuery' in _dict:
            args['expanded_query'] = _dict.get('expandedQuery')
        if 'parsedBoolExpression' in _dict:
            args['parsed_bool_expression'] = BooleanOperands.from_dict(_dict.get('parsedBoolExpression'))
        if 'conceptsExist' in _dict:
            args['concepts_exist'] = _dict.get('conceptsExist')
        if 'cursorId' in _dict:
            args['cursor_id'] = _dict.get('cursorId')
        if 'vocabs' in _dict:
            args['vocabs'] = _dict.get('vocabs')
        if 'annotations' in _dict:
            args['annotations'] = {k : CommonDataModel.from_dict(v) for k,v in _dict.get('annotations').items()}
        if 'metadata' in _dict:
            args['metadata'] = MetadataFields.from_dict(_dict.get('metadata'))
        if 'documents' in _dict:
            args['documents'] = [RankedDocument.from_dict(x) for x in _dict.get('documents')]
        if 'subQueries' in _dict:
            args['sub_queries'] = [SearchModel.from_dict(x) for x in _dict.get('subQueries')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SearchModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'href') and self.href is not None:
            _dict['href'] = self.href
        if hasattr(self, 'page_number') and self.page_number is not None:
            _dict['pageNumber'] = self.page_number
        if hasattr(self, 'get_limit') and self.get_limit is not None:
            _dict['get_limit'] = self.get_limit
        if hasattr(self, 'total_document_count') and self.total_document_count is not None:
            _dict['totalDocumentCount'] = self.total_document_count
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x.to_dict() for x in self.concepts]
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types
        if hasattr(self, 'attributes') and self.attributes is not None:
            _dict['attributes'] = [x.to_dict() for x in self.attributes]
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = [x.to_dict() for x in self.values]
        if hasattr(self, 'ranges') and self.ranges is not None:
            _dict['ranges'] = {k : v.to_dict() for k,v in self.ranges.items()}
        if hasattr(self, 'typeahead') and self.typeahead is not None:
            _dict['typeahead'] = [x.to_dict() for x in self.typeahead]
        if hasattr(self, 'aggregations') and self.aggregations is not None:
            _dict['aggregations'] = self.aggregations
        if hasattr(self, 'date_histograms') and self.date_histograms is not None:
            _dict['dateHistograms'] = self.date_histograms
        if hasattr(self, 'qualifiers') and self.qualifiers is not None:
            _dict['qualifiers'] = [x.to_dict() for x in self.qualifiers]
        if hasattr(self, 'backend') and self.backend is not None:
            _dict['backend'] = self.backend.to_dict()
        if hasattr(self, 'expanded_query') and self.expanded_query is not None:
            _dict['expandedQuery'] = self.expanded_query
        if hasattr(self, 'parsed_bool_expression') and self.parsed_bool_expression is not None:
            _dict['parsedBoolExpression'] = self.parsed_bool_expression.to_dict()
        if hasattr(self, 'concepts_exist') and self.concepts_exist is not None:
            _dict['conceptsExist'] = self.concepts_exist
        if hasattr(self, 'cursor_id') and self.cursor_id is not None:
            _dict['cursorId'] = self.cursor_id
        if hasattr(self, 'vocabs') and self.vocabs is not None:
            _dict['vocabs'] = self.vocabs
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = {k : v.to_dict() for k,v in self.annotations.items()}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'documents') and self.documents is not None:
            _dict['documents'] = [x.to_dict() for x in self.documents]
        if hasattr(self, 'sub_queries') and self.sub_queries is not None:
            _dict['subQueries'] = [x.to_dict() for x in self.sub_queries]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SearchModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SearchModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SearchModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class SentenceModel():
    """
    Object representing a document sentence.

    :attr str document_section: (optional) Document section for sentence.
    :attr StringBuilder text: (optional)
    :attr int begin: (optional) Starting sentence offset.
    :attr int end: (optional) Ending sentence offset.
    :attr int timestamp: (optional) Timestamp of sentence in video transcript.
    """

    def __init__(self, *, document_section: str = None, text: 'StringBuilder' = None, begin: int = None, end: int = None, timestamp: int = None) -> None:
        """
        Initialize a SentenceModel object.

        :param str document_section: (optional) Document section for sentence.
        :param StringBuilder text: (optional)
        :param int begin: (optional) Starting sentence offset.
        :param int end: (optional) Ending sentence offset.
        :param int timestamp: (optional) Timestamp of sentence in video transcript.
        """
        self.document_section = document_section
        self.text = text
        self.begin = begin
        self.end = end
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SentenceModel':
        """Initialize a SentenceModel object from a json dictionary."""
        args = {}
        if 'documentSection' in _dict:
            args['document_section'] = _dict.get('documentSection')
        if 'text' in _dict:
            args['text'] = StringBuilder.from_dict(_dict.get('text'))
        if 'begin' in _dict:
            args['begin'] = _dict.get('begin')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        if 'timestamp' in _dict:
            args['timestamp'] = _dict.get('timestamp')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SentenceModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'document_section') and self.document_section is not None:
            _dict['documentSection'] = self.document_section
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text.to_dict()
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = self.timestamp
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SentenceModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SentenceModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SentenceModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ServiceStatus():
    """
    Object representing service runtime status.

    :attr str version: (optional) version of the service.
    :attr str up_time: (optional) service uptime since last restart.
    :attr str service_state: (optional) scurrent service state.
    :attr str state_details: (optional) service state details.
    :attr str host_name: (optional) service uptime since last restart.
    :attr int request_count: (optional) total number of requests during uptime.
    :attr int max_memory_mb: (optional) Maximum memory used during uptime.
    :attr int commited_memory_mb: (optional) Megabytes of committed memory.
    :attr int in_use_memory_mb: (optional) Megabytes of memory used.
    :attr int available_processors: (optional) number of available processors.
    :attr int concurrent_requests: (optional) number of concurrent requests.
    :attr int max_concurrent_requests: (optional) configured maximum concurrent
          request limit.
    :attr int total_rejected_requests: (optional) number of rejected requests.
    :attr int total_blocked_requests: (optional) number of blocked requests.
    """

    def __init__(self, *, version: str = None, up_time: str = None, service_state: str = None, state_details: str = None, host_name: str = None, request_count: int = None, max_memory_mb: int = None, commited_memory_mb: int = None, in_use_memory_mb: int = None, available_processors: int = None, concurrent_requests: int = None, max_concurrent_requests: int = None, total_rejected_requests: int = None, total_blocked_requests: int = None) -> None:
        """
        Initialize a ServiceStatus object.

        :param str service_state: (optional) scurrent service state.
        :param str state_details: (optional) service state details.
        """

        self.service_state = service_state
        self.state_details = state_details

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceStatus':
        """Initialize a ServiceStatus object from a json dictionary."""
        args = {}
        if 'serviceState' in _dict:
            args['service_state'] = _dict.get('serviceState')
        if 'stateDetails' in _dict:
            args['state_details'] = _dict.get('stateDetails')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'version') and self.version is not None:
            _dict['version'] = self.version
        if hasattr(self, 'up_time') and self.up_time is not None:
            _dict['upTime'] = self.up_time
        if hasattr(self, 'service_state') and self.service_state is not None:
            _dict['serviceState'] = self.service_state
        if hasattr(self, 'state_details') and self.state_details is not None:
            _dict['stateDetails'] = self.state_details
        if hasattr(self, 'host_name') and self.host_name is not None:
            _dict['hostName'] = self.host_name
        if hasattr(self, 'request_count') and self.request_count is not None:
            _dict['requestCount'] = self.request_count
        if hasattr(self, 'max_memory_mb') and self.max_memory_mb is not None:
            _dict['maxMemoryMb'] = self.max_memory_mb
        if hasattr(self, 'commited_memory_mb') and self.commited_memory_mb is not None:
            _dict['commitedMemoryMb'] = self.commited_memory_mb
        if hasattr(self, 'in_use_memory_mb') and self.in_use_memory_mb is not None:
            _dict['inUseMemoryMb'] = self.in_use_memory_mb
        if hasattr(self, 'available_processors') and self.available_processors is not None:
            _dict['availableProcessors'] = self.available_processors
        if hasattr(self, 'concurrent_requests') and self.concurrent_requests is not None:
            _dict['concurrentRequests'] = self.concurrent_requests
        if hasattr(self, 'max_concurrent_requests') and self.max_concurrent_requests is not None:
            _dict['maxConcurrentRequests'] = self.max_concurrent_requests
        if hasattr(self, 'total_rejected_requests') and self.total_rejected_requests is not None:
            _dict['totalRejectedRequests'] = self.total_rejected_requests
        if hasattr(self, 'total_blocked_requests') and self.total_blocked_requests is not None:
            _dict['totalBlockedRequests'] = self.total_blocked_requests
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    
    class ServiceStateEnum(Enum):
        """
        scurrent service state.
        """
        OK = "OK"
        WARNING = "WARNING"
        ERROR = "ERROR"


class SortEntry(object):
    """
    Object representing sort preference.
    :attr str field: field to sort on
    :attr Order sortOrder: sort direction
    """

    def __init__(self, field, sort_order):
        """
        Initialize a SortEntry object.
        :param str field: field to sort on
        :param Order sortOrder: sort direction
        """
        self.field = field
        self.sort_order = sort_order

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ServiceStatus object from a json dictionary."""
        args = {}
        if 'field' in _dict:
            args['field'] = _dict.get('field')
        if 'sortOrder' in _dict:
            args['sort_order'] = Order._from_dict(_dict.get('sortOrder'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'field') and self.field is not None:
            _dict['field'] = self.field
        if hasattr(self, 'sort_order') and self.sort_order is not None:
            _dict['sortOrder'] = self.sort_order._to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this ServiceStatus object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class StringBuilder():
    """
    StringBuilder.

    """

    def __init__(self) -> None:
        """
        Initialize a StringBuilder object.

        """

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'StringBuilder':
        """Initialize a StringBuilder object from a json dictionary."""

        args = {}
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a StringBuilder object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this StringBuilder object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'StringBuilder') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'StringBuilder') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Supports(object):
    """
    Supports.
    :attr list[str] supports: (optional)
    """

    def __init__(self, supports=None):
        """
        Initialize a Supports object.
        :param list[str] supports: (optional)
        """
        self.supports = supports

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Supports object from a json dictionary."""
        args = {}
        if 'supports' in _dict:
            args['supports'] = _dict.get('supports')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'supports') and self.supports is not None:
            _dict['supports'] = self.supports
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Supports object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class TextSpan():
    """
    Objeft representing a document text span.

    :attr str section: (optional) Document section where artifact was found.
    :attr int begin: (optional) Start of text span.
    :attr int end: (optional) End of text span.
    :attr str covered_text: (optional) Covered text span.
    :attr str source: (optional) Documemnt provider.
    :attr str type: (optional) Text span type.
    """

    def __init__(self, *, section: str = None, begin: int = None, end: int = None, covered_text: str = None, source: str = None, type: str = None) -> None:
        """
        Initialize a TextSpan object.

        :param str section: (optional) Document section where artifact was found.
        :param int begin: (optional) Start of text span.
        :param int end: (optional) End of text span.
        :param str covered_text: (optional) Covered text span.
        :param str source: (optional) Documemnt provider.
        :param str type: (optional) Text span type.
        """
        self.section = section
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.source = source
        self.type = type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'TextSpan':
        """Initialize a TextSpan object from a json dictionary."""
        args = {}
        if 'section' in _dict:
            args['section'] = _dict.get('section')
        if 'begin' in _dict:
            args['begin'] = _dict.get('begin')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        if 'coveredText' in _dict:
            args['covered_text'] = _dict.get('coveredText')
        if 'source' in _dict:
            args['source'] = _dict.get('source')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a TextSpan object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'section') and self.section is not None:
            _dict['section'] = self.section
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this TextSpan object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'TextSpan') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'TextSpan') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Title(object):
    """
    Title.
    :attr int boost: (optional)
    """

    def __init__(self, boost=None):
        """
        Initialize a Title object.
        :param int boost: (optional)
        """
        self.boost = boost

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Title object from a json dictionary."""
        args = {}
        if 'boost' in _dict:
            args['boost'] = _dict.get('boost')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'boost') and self.boost is not None:
            _dict['boost'] = self.boost
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Title object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Typeahead(object):
    """
    Typeahead.
    :attr str ontology: (optional)
    :attr str query: (optional)
    :attr list[str] types: (optional)
    :attr int limit: (optional)
    :attr bool no_duplicates: (optional)
    """

    def __init__(self, ontology=None, query=None, types=None, limit=None, no_duplicates=None):
        """
        Initialize a Typeahead object.
        :param str ontology: (optional)
        :param str query: (optional)
        :param list[str] types: (optional)
        :param int limit: (optional)
        :param bool no_duplicates: (optional)
        """
        self.ontology = ontology
        self.query = query
        self.types = types
        self.limit = limit
        self.no_duplicates = no_duplicates

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Typeahead object from a json dictionary."""
        args = {}
        if 'ontology' in _dict:
            args['ontology'] = _dict.get('ontology')
        if 'query' in _dict:
            args['query'] = _dict.get('query')
        if 'types' in _dict:
            args['types'] = _dict.get('types')
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'noDuplicates' in _dict:
            args['no_duplicates'] = _dict.get('noDuplicates')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'ontology') and self.ontology is not None:
            _dict['ontology'] = self.ontology
        if hasattr(self, 'query') and self.query is not None:
            _dict['query'] = self.query
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'no_duplicates') and self.no_duplicates is not None:
            _dict['noDuplicates'] = self.no_duplicates
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Typeahead object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class TypesModel(object):
    """
    List of ontology semantic types.
    :attr list[str] types: (optional) List of ontology defined semantic types.
    """

    def __init__(self, types=None):
        """
        Initialize a TypesModel object.
        :param list[str] types: (optional) List of ontology defined semantic types.
        """
        self.types = types

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a TypesModel object from a json dictionary."""
        args = {}
        if 'types' in _dict:
            args['types'] = _dict.get('types')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'types') and self.types is not None:
            _dict['types'] = self.types
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this TypesModel object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class UnstructuredModel():
    """
    Model representing unstructed text.

    :attr str text: (optional) Text of the document.
    :attr DataModel data: (optional) Model representing ontology artifacts.
    """

    def __init__(self, *, text: str = None, data: 'DataModel' = None) -> None:
        """
        Initialize a UnstructuredModel object.

        :param str text: (optional) Text of the document.
        :param DataModel data: (optional) Model representing ontology artifacts.
        """
        self.text = text
        self.data = data

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UnstructuredModel':
        """Initialize a UnstructuredModel object from a json dictionary."""
        args = {}
        if 'text' in _dict:
            args['text'] = _dict.get('text')
        if 'data' in _dict:
            args['data'] = DataModel.from_dict(_dict.get('data'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UnstructuredModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text
        if hasattr(self, 'data') and self.data is not None:
            _dict['data'] = self.data.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UnstructuredModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UnstructuredModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UnstructuredModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Values(object):
    """
    Values.
    :attr str attribute_id: (optional)
    :attr str unit: (optional)
    :attr str scope: (optional)
    """

    def __init__(self, attribute_id=None, unit=None, scope=None):
        """
        Initialize a Values object.
        :param str attribute_id: (optional)
        :param str unit: (optional)
        :param str scope: (optional)
        """
        self.attribute_id = attribute_id
        self.unit = unit
        self.scope = scope

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Values object from a json dictionary."""
        args = {}
        if 'attributeId' in _dict:
            args['attribute_id'] = _dict.get('attributeId')
        if 'unit' in _dict:
            args['unit'] = _dict.get('unit')
        if 'scope' in _dict:
            args['scope'] = _dict.get('scope')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'attribute_id') and self.attribute_id is not None:
            _dict['attributeId'] = self.attribute_id
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'scope') and self.scope is not None:
            _dict['scope'] = self.scope
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Values object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class YearAndHits(object):
    """
    YearAndHits.
    :attr str date: (optional)
    :attr int hits: (optional)
    """

    def __init__(self, date=None, hits=None):
        """
        Initialize a YearAndHits object.
        :param str date: (optional)
        :param int hits: (optional)
        """
        self.date = date
        self.hits = hits

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a YearAndHits object from a json dictionary."""
        args = {}
        if 'date' in _dict:
            args['date'] = _dict.get('date')
        if 'hits' in _dict:
            args['hits'] = _dict.get('hits')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AggregationModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'date') and self.date is not None:
            _dict['date'] = self.date
        if hasattr(self, 'hits') and self.hits is not None:
            _dict['hits'] = self.hits
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this YearAndHits object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other
