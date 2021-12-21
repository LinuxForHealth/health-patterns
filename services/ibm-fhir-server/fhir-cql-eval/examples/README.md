This folder contains example implementations that use the fhir-cql image to evaluate cql expressions and libraries.


##### CQLDemoNotebook.ipynb
CPGCQL and CPGLibraryEvaluate

- OPERATION: CPGCQL

  - The official URL for this operation definition is:http://hl7.org/fhir/uv/cpg/OperationDefinition/cpg-cql

  - Evaluates a CQL expression and returns the results as a Parameters resource.

  - URL: [base]/$cql




- OPERATION: CPGLibraryEvaluate

  - The official URL for this operation definition is:http://hl7.org/fhir/uv/cpg/OperationDefinition/cpg-library-evaluate

  - Evaluates the contents of a library and returns the results as a Parameters resource.

  - URL: [base]/Library/$evaluate

  - URL: [base]/Library/[id]/$evaluate


Notebook cells contain prerequisite, setup, patient loading, and cql execution.
