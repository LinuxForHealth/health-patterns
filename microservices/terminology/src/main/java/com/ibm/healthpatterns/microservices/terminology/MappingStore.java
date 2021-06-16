package com.ibm.healthpatterns.microservices.terminology;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.IOUtils;
import org.jboss.logging.Logger;

import java.io.*;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.*;
import java.util.stream.Collectors;

public class MappingStore {

    private static final Logger logger = Logger.getLogger(MappingStore.class);
    /**
     * Directory in the classpath that has the default mappings FHIR resources
     */
    public static final String MAPPINGS_DIRECTORY = "/defaultMappings/";

    /**
     * File that has the default StructureDefinition to ValueSet mappings
     */
    public static final String SD_TO_VS_MAPPINGS_FILE = "/defaultMappings/structureDefinition.mappings";

    /**
     * The FHIR Resources used for the default terminology mapping from US Core Birth Sex to IBM CDM Sex Assigned at Birth
     */
    private static final String[] DEFAULT_MAPPING_RESOURCES = new String[] {"cdm-sex-assigned-at-birth-vs.json", "uscore-birthsex-vs.json", "uscore-to-cdm-cm.json"};

    private final File structureDefinitionFile;
    private final Map<String, String> valueSetMappings;
    private final Map<String, String> savedResourcesMapping;
    private final File mappingsDir;
    public boolean canReadWriteToDisk;
    private final InputStream defaultSDFile;
    private final ObjectMapper jsonDeserializer;

    public MappingStore(File structureDefinitionFile, File mappingsDir){
        this.structureDefinitionFile = structureDefinitionFile;
        this.mappingsDir = mappingsDir;
        this.defaultSDFile = this.getClass().getResourceAsStream(SD_TO_VS_MAPPINGS_FILE);
        this.savedResourcesMapping = new HashMap<>();
        this.valueSetMappings = new HashMap<>();
        this.jsonDeserializer = new ObjectMapper();
        try {
            boolean initialize = false;
            if (structureDefinitionFile != null && mappingsDir != null) {
                if (!structureDefinitionFile.exists()) {
                    structureDefinitionFile.createNewFile();
                    initialize = true;
                }
                if (!mappingsDir.exists()) {
                    mappingsDir.mkdirs();
                    initialize = true;
                }
                this.canReadWriteToDisk = structureDefinitionFile.isFile() && structureDefinitionFile.canRead() &&
                        structureDefinitionFile.canWrite() && mappingsDir.isDirectory() &&
                        mappingsDir.canWrite() && mappingsDir.canRead();
                if (canReadWriteToDisk) {
                    logger.info("Terminology service accessing disk.");
                } else {
                    logger.info("Terminology service cannot access disk, changes will be transient.");
                }
            } else {
                this.canReadWriteToDisk = false;
            }
            if (initialize & canReadWriteToDisk) {
                copyDefaultResourcesToDisk();
            }
        } catch (IOException e) {
            canReadWriteToDisk = false;
        }

        if (this.canReadWriteToDisk) {
            // pull the resources currently saved to mappings dir
            File[] mappingFiles = mappingsDir.listFiles();
            assert mappingFiles != null;
            for (File mappingFile : mappingFiles) {
                try {
                    savedResourcesMapping.put(mappingFile.getName(), IOUtils.toString(new FileInputStream(mappingFile), Charset.defaultCharset()));
                } catch (IOException e) {
                    System.err.println("Could not read the FHIR mapping resource: " + mappingFile.getName() + ", the Terminology Service might not be functional: " + e.getMessage());
                }
            }
            // add structureDefinitions from file into map.
            try {
                initializeStructureDefinition(new FileInputStream(structureDefinitionFile));
            } catch (IOException e) {
                System.err.println("Could not read the structure definition file: the Terminology Service will not be functional: " + e.getMessage());
            }
        } else {
            // pull default resources
            for(String fileName : DEFAULT_MAPPING_RESOURCES) {
                InputStream configInputStream = this.getClass().getResourceAsStream(MAPPINGS_DIRECTORY + fileName);
                try {
                    assert configInputStream != null;
                    savedResourcesMapping.put(fileName, IOUtils.toString(configInputStream, Charset.defaultCharset()));
                } catch (IOException e) {
                    System.err.println("Could not read default FHIR mapping resource: " + fileName + ", the Terminology Service won't be functional: " + e.getMessage());
                }
            }
            // add default structureDefinition map
            initializeStructureDefinition(defaultSDFile);
        }
    }

    public void copyDefaultResourcesToDisk() {
        if (canReadWriteToDisk) {
            for (String fileName : DEFAULT_MAPPING_RESOURCES) {
                InputStream configInputStream = this.getClass().getResourceAsStream(MAPPINGS_DIRECTORY + fileName);
                try {
                    assert configInputStream != null;
                    String mapping = IOUtils.toString(configInputStream, Charset.defaultCharset());
                    saveMapping(fileName, mapping);
                } catch (IOException e) {
                    System.err.println("Could not read default FHIR mapping resource: " + fileName + ", the Terminology Service won't be functional: " + e.getMessage());
                }
            }
            try {
                Files.copy(defaultSDFile, structureDefinitionFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                initializeStructureDefinition(new FileInputStream(structureDefinitionFile));
            } catch (IOException e) {
                System.err.println("Could not read default structure definition file, the terminology service will not work");
                e.printStackTrace();
            }
        }
    }

    public void saveMapping(String mappingName, String mapping) {
        if (canReadWriteToDisk) {
            JsonNode jsonNode;
            try {
                jsonNode = jsonDeserializer.readTree(mapping);
                File mappingFile = new File(mappingsDir + mappingName);
                BufferedWriter out = new BufferedWriter(new FileWriter(mappingFile, false));
                out.write(jsonNode.toPrettyString());
                out.close();
            } catch (IOException e) {
                //error?
            }
        }
        savedResourcesMapping.put(mappingName, mapping);
    }

    public void deleteMapping(String mappingName) {
        if (canReadWriteToDisk) {
            File mappingFile = new File(mappingsDir + mappingName);
            if (mappingExists(mappingName) && mappingFile.exists()) {
                boolean deleted = mappingFile.delete();
                if (deleted) {
                    logger.info("Mapping file " + mappingName + " deleted");
                    savedResourcesMapping.remove(mappingName);
                } else {
                    logger.warn("Error deleting mapping " + mappingName + ".");
                }
            }
        } else {
            savedResourcesMapping.remove(mappingName);
        }
    }

    public boolean mappingExists(String mappingName) {
        return savedResourcesMapping.containsKey(mappingName);
    }

    public String getMapping(String mappingName) {
        return savedResourcesMapping.get(mappingName);
    }

    public Map<String, String> getSavedResourcesMapping() {
        return savedResourcesMapping;
    }

    /**
     * Adds a bi-directional relationship between a StructureDefinition and its corresponding ValueSet.
     * <p>
     * A bi-directional relationship is needed because this class will need to know the VS for an incoming
     * codeValue given its StructuredDefinition url, and after translating it to its corresponding VS it
     * will need to get the corresponding SD and set it as the new url.
     *
     * @param sdUri the URI for the StructureDefinition
     * @param vsUri the URI for the ValueSet
     */
    public void addSDMapping(String sdUri, String vsUri) {

        valueSetMappings.put(sdUri, vsUri);
        valueSetMappings.put(vsUri, sdUri);
        boolean duplicate = containsSDMapping(sdUri, vsUri);
        if (canReadWriteToDisk) {
            if (!duplicate) {
                try (BufferedWriter out = new BufferedWriter(new FileWriter(structureDefinitionFile, true))) {
                    out.write("\n" + sdUri + " <=> " + vsUri);
                } catch (IOException e) {
                    //error?
                }
            }
        }
    }

    public boolean containsSDMapping(String sdUri, String vsUri) {
        boolean duplicate = false;
        if (canReadWriteToDisk) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(structureDefinitionFile), StandardCharsets.UTF_8))) {
                for (String line : reader.lines().collect(Collectors.toList())) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) {
                        continue;
                    }
                    String[] structureDefinitionToValueSet = line.split("<=>");
                    if (structureDefinitionToValueSet.length != 2) {
                        System.err.println("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    }
                    if (structureDefinitionToValueSet[0].trim().equals(sdUri) && structureDefinitionToValueSet[1].trim().equals(vsUri) ||
                            structureDefinitionToValueSet[1].trim().equals(sdUri) && structureDefinitionToValueSet[0].trim().equals(vsUri)) {
                        duplicate = true;
                        break;
                    }
                }

            } catch (IOException e) {
                System.err.println("Could not read StructuredDefinition to ValueSet configuration mapping file: the Terminology Service won't be functional: " + e.getMessage());
            }
        }
        return valueSetMappings.containsKey(sdUri) && valueSetMappings.get(sdUri).equals(vsUri) && duplicate;
    }

    public void deleteSDMapping(String sdUri, String vsUri) {
        if (containsSDMapping(sdUri,vsUri)) {
            valueSetMappings.remove(sdUri);
            valueSetMappings.remove(vsUri);
            if (canReadWriteToDisk) {
                List<String> lines = new ArrayList<>();
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(structureDefinitionFile), StandardCharsets.UTF_8))) {
                    lines.addAll(reader.lines().collect(Collectors.toList()));
                } catch (IOException e) {
                    System.err.println("Could not read StructuredDefinition to ValueSet configuration mapping file: the Terminology Service won't be functional: " + e.getMessage());
                }
                String lineToDelete = null;
                for (String line: lines) {
                    String lineCopy = line.trim();
                    if (lineCopy.startsWith("#") || lineCopy.isBlank()) {
                        continue;
                    }
                    String[] structureDefinitionToValueSet = lineCopy.split("<=>");
                    if (structureDefinitionToValueSet.length != 2) {
                        System.err.println("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    } else if(structureDefinitionToValueSet[0].trim().equals(sdUri) && structureDefinitionToValueSet[1].trim().equals(vsUri) ||
                            structureDefinitionToValueSet[1].trim().equals(sdUri) && structureDefinitionToValueSet[0].trim().equals(vsUri)) {
                        lineToDelete = line;
                    }
                }
                if (lineToDelete != null) {
                    lines.remove(lineToDelete);
                    try (BufferedWriter out = new BufferedWriter(new FileWriter(structureDefinitionFile, false))) {
                        for (String line: lines) {
                            out.write(line);
                            out.write("\n");
                        }
                    } catch (IOException e) {
                        //error?
                    }
                }

            }
        }
    }

    public Set<String> getAllStructureDefinitions() {
        HashSet<String> output = new HashSet<>();
        for ( String left: valueSetMappings.keySet()){
            String right = valueSetMappings.get(left);
            if (left.compareTo(right) <= 0) {
                output.add(left + " <=> " + right);
            } else {
                output.add(right + " <=> " + left);
            }
        }
        return output;
    }

    /**
     * pulls the mappings from the structure definition file into the valueSetMapping map.
     */
    public void initializeStructureDefinition(InputStream mappingInputStream) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(mappingInputStream, StandardCharsets.UTF_8))) {
            reader.lines().forEach(line -> {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    return;
                }
                String[] structureDefinitionToValueSet = line.split("<=>");
                if (structureDefinitionToValueSet.length != 2) {
                    System.err.println("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    return;
                }
                addSDMapping(structureDefinitionToValueSet[0].trim(), structureDefinitionToValueSet[1].trim());
            });
        } catch (IOException e) {
            System.err.println("Could not read StructuredDefinition to ValueSet configuration mapping file: the Terminology Service won't be functional: " + e.getMessage());
        }
    }

    public Map<String, String> getValueSetMapping() {
        return valueSetMappings;
    }
}
