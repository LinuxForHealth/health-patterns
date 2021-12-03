# Copyright 2021 IBM All Rights Reserved.
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
"""Utilities for working with UMLS concept types

   A UMLS concept has a unique ID for each semantic type, a service
   such as QuickUMLS will often return these unique id as candidate
   semantic types associated with a cui.

   This module defines mappings between type ids and type names, as well
   as a way to determine which type names are relevant to concept reference
   types.

"""

from typing import Dict
from typing import Iterable
from typing import List
from typing import Set
from typing import Type
from typing import TypeVar

from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.resource import Resource

from text_analytics.insight_source.fields_of_interest import CodeableConceptRefType

# UMLS Type ID such as T116 or T020
UmlsTypeId = str

# UMLS Type Name such as umls.Activity
UmlsTypeName = str

_type_id_to_type_name: Dict[UmlsTypeId, UmlsTypeName] = {
    "T116": "umls.AminoAcidPeptideOrProtein",
    "T020": "umls.AcquiredAbnormality",
    "T052": "umls.Activity",
    "T100": "umls.AgeGroup",
    "T087": "umls.AminoAcidSequence",
    "T011": "umls.Amphibian",
    "T190": "umls.AnatomicalAbnormality",
    "T008": "umls.Animal",
    "T017": "umls.AnatomicalStructure",
    "T195": "umls.Antibiotic",
    "T194": "umls.Archaeon",
    "T123": "umls.BiologicallyActiveSubstance",
    "T007": "umls.Bacterium",
    "T031": "umls.BodySubstance",
    "T022": "umls.BodySystem",
    "T053": "umls.Behavior",
    "T038": "umls.BiologicFunction",
    "T012": "umls.Bird",
    "T029": "umls.BodyLocationOrRegion",
    "T091": "umls.BiomedicalOccupationOrDiscipline",
    "T122": "umls.BiomedicalOrDentalMaterial",
    "T023": "umls.BodyPartOrganOrOrganComponent",
    "T030": "umls.BodySpaceOrJunction",
    "T026": "umls.CellComponent",
    "T043": "umls.CellFunction",
    "T025": "umls.Cell",
    "T019": "umls.CongenitalAbnormality",
    "T103": "umls.Chemical",
    "T120": "umls.ChemicalViewedFunctionally",
    "T104": "umls.ChemicalViewedStructurally",
    "T185": "umls.Classification",
    "T201": "umls.ClinicalAttribute",
    "T200": "umls.ClinicalDrug",
    "T077": "umls.ConceptualEntity",
    "T049": "umls.CellOrMolecularDysfunction",
    "T088": "umls.CarbohydrateSequence",
    "T060": "umls.DiagnosticProcedure",
    "T056": "umls.DailyOrRecreationalActivity",
    "T203": "umls.DrugDeliveryDevice",
    "T047": "umls.DiseaseOrSyndrome",
    "T065": "umls.EducationalActivity",
    "T069": "umls.EnvironmentalEffectOfHumans",
    "T196": "umls.ElementIonOrIsotope",
    "T050": "umls.ExperimentalModelOfDisease",
    "T018": "umls.EmbryonicStructure",
    "T071": "umls.Entity",
    "T126": "umls.Enzyme",
    "T204": "umls.Eukaryote",
    "T051": "umls.Event",
    "T099": "umls.Family Group",
    "T021": "umls.FullyFormedAnatomicalStructure",
    "T013": "umls.Fish",
    "T033": "umls.Finding",
    "T004": "umls.Fungus",
    "T168": "umls.Food",
    "T169": "umls.FunctionalConcept",
    "T045": "umls.GeneticFunction",
    "T083": "umls.GeographicArea",
    "T028": "umls.GeneOrGenome",
    "T064": "umls.GovernmentalOrRegulatoryActivity",
    "T102": "umls.GroupAttribute",
    "T096": "umls.Group",
    "T068": "umls.Human-causedPhenomenonOrProcess",
    "T093": "umls.HealthCareRelatedOrganization",
    "T058": "umls.HealthCareActivity",
    "T131": "umls.HazardousOrPoisonousSubstance",
    "T125": "umls.Hormone",
    "T016": "umls.Human",
    "T078": "umls.IdeaOrConcept",
    "T129": "umls.ImmunologicFactor",
    "T055": "umls.IndividualBehavior",
    "T197": "umls.InorganicChemical",
    "T037": "umls.InjuryOrPoisoning",
    "T170": "umls.IntellectualProduct",
    "T130": "umls.IndicatorReagentOrDiagnosticAid",
    "T171": "umls.Language",
    "T059": "umls.LaboratoryProcedure",
    "T034": "umls.LaboratoryOrTestResult",
    "T015": "umls.Mammal",
    "T063": "umls.MolecularBiologyResearchTechnique",
    "T066": "umls.MachineActivity",
    "T074": "umls.MedicalDevice",
    "T041": "umls.MentalProcess",
    "T073": "umls.ManufacturedObject",
    "T048": "umls.MentalOrBehavioralDysfunction",
    "T044": "umls.MolecularFunction",
    "T085": "umls.MolecularSequence",
    "T191": "umls.NeoplasticProcess",
    "T114": "umls.NucleicAcidNucleosideOrNucleotide",
    "T070": "umls.NaturalPhenomenonOrProcess",
    "T086": "umls.NucleotideSequence",
    "T057": "umls.OccupationalActivity",
    "T090": "umls.OccupationOrDiscipline",
    "T109": "umls.OrganicChemical",
    "T032": "umls.OrganismAttribute",
    "T040": "umls.OrganismFunction",
    "T001": "umls.Organism",
    "T092": "umls.Organization",
    "T042": "umls.OrganOrTissueFunction",
    "T046": "umls.PathologicFunction",
    "T072": "umls.PhysicalObject",
    "T067": "umls.PhenomenonOrProcess",
    "T039": "umls.PhysiologicFunction",
    "T121": "umls.PharmacologicSubstance",
    "T002": "umls.Plant",
    "T101": "umls.PatientOrDisabledGroup",
    "T098": "umls.PopulationGroup",
    "T097": "umls.ProfessionalOrOccupationalGroup",
    "T094": "umls.ProfessionalSociety",
    "T080": "umls.QualitativeConcept",
    "T081": "umls.QuantitativeConcept",
    "T192": "umls.Receptor",
    "T014": "umls.Reptile",
    "T062": "umls.ResearchActivity",
    "T075": "umls.ResearchDevice",
    "T089": "umls.RegulationOrLaw",
    "T167": "umls.Substance",
    "T095": "umls.Self-helpOrReliefOrganization",
    "T054": "umls.SocialBehavior",
    "T184": "umls.SignOrSymptom",
    "T082": "umls.SpatialConcept",
    "T024": "umls.Tissue",
    "T079": "umls.TemporalConcept",
    "T061": "umls.TherapeuticOrPreventiveProcedure",
    "T005": "umls.Virus",
    "T127": "umls.Vitamin",
    "T010": "umls.Vertebrate",
}


CONDITION_TYPES: List[UmlsTypeName] = [
    "umls.DiseaseOrSyndrome",
    "umls.PathologicFunction",
    "umls.SignOrSymptom",
    "umls.NeoplasticProcess",
    "umls.CellOrMolecularDysfunction",
    "umls.MentalOrBehavioralDysfunction",
]


MEDICATION_TYPES: List[UmlsTypeName] = [
    "umls.Antibiotic",
    "umls.ClinicalDrug",
    "umls.PharmacologicSubstance",
    "umls.OrganicChemical",
]


VACCINE_TYPES: List[UmlsTypeName] = ["umls.ImmunologicFactor"]


ALLERGEN_TYPES: List[UmlsTypeName] = [
    "umls.DiseaseOrSyndrome",
    "umls.PathologicFunction",
    "umls.SignOrSymptom",
]


_resource_type_to_type_names: Dict[str, List[UmlsTypeName]] = {
    Condition.__name__: CONDITION_TYPES,
    MedicationStatement.__name__: MEDICATION_TYPES,
}


_concept_type_to_type_names: Dict[CodeableConceptRefType, List[UmlsTypeName]] = {
    CodeableConceptRefType.ALLERGEN: ALLERGEN_TYPES,
    CodeableConceptRefType.CONDITION: CONDITION_TYPES,
    CodeableConceptRefType.MANIFESTATION: [],
    CodeableConceptRefType.VACCINE: VACCINE_TYPES,
}


ExtendsResource = TypeVar("ExtendsResource", bound=Resource)


def resource_relevant_to_any_type_names(
    resource_clazz: Type[ExtendsResource], type_names: Iterable[UmlsTypeName]
) -> bool:
    """Determine if any of the type names are relevant to the given resource class

    Args:
        resource - the fhir resource
        type_names - the names of types to consider

    Returns:
        true if any of the type names are relevant

    Example:
    >>> resource_relevant_to_any_type_names(Condition, ["umls.DiseaseOrSyndrome", "umls.ImmunologicFactor"])
    True
    """
    relevant_type_names = _resource_type_to_type_names.get(resource_clazz.__name__)
    if relevant_type_names:
        return any(name in relevant_type_names for name in type_names)
    return False


def ref_type_relevant_to_any_type_names(
    ref_type: CodeableConceptRefType, type_names: Iterable[UmlsTypeName]
) -> bool:
    """Determine if any of the type names are relevant for the given concept type

    Args:
        ref_type - the type of reference
        type_names - the names of types to consider

    Returns:
        true if any of the type names are relevant

    Example:
    >>> ref_type_relevant_to_any_type_names(CodeableConceptRefType.VACCINE, ["umls.ImmunologicFactor"])
    True
    """
    relevant_type_names = _concept_type_to_type_names.get(ref_type)
    if relevant_type_names:
        return any(name in relevant_type_names for name in type_names)
    return False


def get_names_from_type_ids(ids: Iterable[UmlsTypeId]) -> Set[UmlsTypeName]:
    """
    For a list of UMLS semantic network type ids, return more readable names

    These names could be used in a wider vocabulary than UMLS

    Args: ids - type ids
    Returns: list of readable names

    Example:
    >>> t = get_names_from_type_ids(['T047', 'T046'])
    >>> t == {'umls.PathologicFunction', 'umls.DiseaseOrSyndrome'}
    True
    """
    return set(
        _type_id_to_type_name[tid] for tid in ids if tid in _type_id_to_type_name
    )
