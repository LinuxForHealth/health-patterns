semTypes = {"T116": "Amino Acid, Peptide, or Protein",
            "T020": "Acquired Abnormality",
            "T052": "Activity",
            "T100": "Age Group",
            "T087": "Amino Acid Sequence",
            "T011": "Amphibian",
            "T190": "Anatomical Abnormality",
            "T008": "Animal",
            "T017": "Anatomical Structure",
            "T195": "Antibiotic",
            "T194": "Archaeon",
            "T123": "Biologically Active Substance",
            "T007": "Bacterium",
            "T031": "Body Substance",
            "T022": "Body System",
            "T053": "Behavior",
            "T038": "Biologic Function",
            "T012": "Bird",
            "T029": "Body Location or Region",
            "T091": "Biomedical Occupation or Discipline",
            "T122": "Biomedical or Dental Material",
            "T023": "Body Part, Organ, or Organ Component",
            "T030": "Body Space or Junction",
            "T026": "Cell Component",
            "T043": "Cell Function",
            "T025": "Cell",
            "T019": "Congenital Abnormality",
            "T103": "Chemical",
            "T120": "Chemical Viewed Functionally",
            "T104": "Chemical Viewed Structurally",
            "T185": "Classification",
            "T201": "Clinical Attribute",
            "T200": "Clinical Drug",
            "T077": "Conceptual Entity",
            "T049": "Cell or Molecular Dysfunction",
            "T088": "Carbohydrate Sequence",
            "T060": "Diagnostic Procedure",
            "T056": "Daily or Recreational Activity",
            "T203": "Drug Delivery Device",
            "T047": "Disease or Syndrome",
            "T065": "Educational Activity",
            "T069": "Environmental Effect of Humans",
            "T196": "Element, Ion, or Isotope",
            "T050": "Experimental Model of Disease",
            "T018": "Embryonic Structure",
            "T071": "Entity",
            "T126": "Enzyme",
            "T204": "Eukaryote",
            "T051": "Event",
            "T099": "Family Group",
            "T021": "Fully Formed Anatomical Structure",
            "T013": "Fish",
            "T033": "Finding",
            "T004": "Fungus",
            "T168": "Food",
            "T169": "Functional Concept",
            "T045": "Genetic Function",
            "T083": "Geographic Area",
            "T028": "Gene or Genome",
            "T064": "Governmental or Regulatory Activity",
            "T102": "Group Attribute",
            "T096": "Group",
            "T068": "Human-caused Phenomenon or Process",
            "T093": "Health Care Related Organization",
            "T058": "Health Care Activity",
            "T131": "Hazardous or Poisonous Substance",
            "T125": "Hormone",
            "T016": "Human",
            "T078": "Idea or Concept",
            "T129": "Immunologic Factor",
            "T055": "Individual Behavior",
            "T197": "Inorganic Chemical",
            "T037": "Injury or Poisoning",
            "T170": "Intellectual Product",
            "T130": "Indicator, Reagent, or Diagnostic Aid",
            "T171": "Language",
            "T059": "Laboratory Procedure",
            "T034": "Laboratory or Test Result",
            "T015": "Mammal",
            "T063": "Molecular Biology Research Technique",
            "T066": "Machine Activity",
            "T074": "Medical Device",
            "T041": "Mental Process",
            "T073": "Manufactured Object",
            "T048": "Mental or Behavioral Dysfunction",
            "T044": "Molecular Function",
            "T085": "Molecular Sequence",
            "T191": "Neoplastic Process",
            "T114": "Nucleic Acid, Nucleoside, or Nucleotide",
            "T070": "Natural Phenomenon or Process",
            "T086": "Nucleotide Sequence",
            "T057": "Occupational Activity",
            "T090": "Occupation or Discipline",
            "T109": "Organic Chemical",
            "T032": "Organism Attribute",
            "T040": "Organism Function",
            "T001": "Organism",
            "T092": "Organization",
            "T042": "Organ or Tissue Function",
            "T046": "Pathologic Function",
            "T072": "Physical Object",
            "T067": "Phenomenon or Process",
            "T039": "Physiologic Function",
            "T121": "Pharmacologic Substance",
            "T002": "Plant",
            "T101": "Patient or Disabled Group",
            "T098": "Population Group",
            "T097": "Professional or Occupational Group",
            "T094": "Professional Society",
            "T080": "Qualitative Concept",
            "T081": "Quantitative Concept",
            "T192": "Receptor",
            "T014": "Reptile",
            "T062": "Research Activity",
            "T075": "Research Device",
            "T089": "Regulation or Law",
            "T167": "Substance",
            "T095": "Self-help or Relief Organization",
            "T054": "Social Behavior",
            "T184": "Sign or Symptom",
            "T082": "Spatial Concept",
            "T024": "Tissue",
            "T079": "Temporal Concept",
            "T061": "Therapeutic or Preventive Procedure",
            "T005": "Virus",
            "T127": "Vitamin",
            "T010": "Vertebrate"}


def lookup(semtype_code):
    if semTypes.keys().__contains__(semtype_code):
        return semTypes.get(semtype_code)
    return semtype_code
