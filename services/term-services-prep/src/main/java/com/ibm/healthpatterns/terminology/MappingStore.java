package com.ibm.healthpatterns.terminology;

/**
 * A {@link MappingStore} manages the storage and retrieval of Mappings and Structure Definitions for
 * a {@link TerminologyService} wrapped by {@link TerminologyRest}, both in memory and to disk. This
 * class requires the information for where the Mappings and Structure Definitions are stored.
 *
 * @author Bryce Hall
 */

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.IOUtils;
import org.jboss.logging.Logger;
import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;

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

    private final ObjectMapper jsonDeserializer;

    private final File structureDefinitionFile;

    private final File mappingsDir;

    private final InputStream defaultSDFile;

    private final BiMap<String, String> structureDefinitions;

    private final Map<String, String> savedMappings;

    private boolean canAccessDisc;


    /**
     * Initializes the MappingStore with the given structureDefinitionFile and mappingsDir pointing to the corresponding
     * locations on the disc/persistent volume.
     * If the given files are inaccessible, the MappingStore operates in memory only mode, so changes are not persisted.
     * If the given files have not been created yet, the MappingStore firsts initializes them using the default resources.
     * The MappingStore pulls the mappings and structure definitions into memory from the disc (or the default resources
     * if the disc is inaccessible) then allows for further mappings and structure definitions to be
     * added/deleted/accessed as needed.  If the disc is accessible, such changes will be reflected in the files stored
     * on disc.
     * @param structureDefinitionFile the file where structuredefinitions should be stored on disc, or null if running
     *                                in memory-only mode.
     * @param mappingsDir the directory where mappings should be stored on disc, or null if running in memory-only mode.
     */
    public MappingStore(File structureDefinitionFile, File mappingsDir) {
        this.structureDefinitionFile = structureDefinitionFile;
        this.mappingsDir = mappingsDir;
        this.defaultSDFile = this.getClass().getResourceAsStream(SD_TO_VS_MAPPINGS_FILE);
        this.savedMappings = new HashMap<>();
        this.structureDefinitions = HashBiMap.create();
        this.jsonDeserializer = new ObjectMapper();
        try {
            boolean initialize = false;
            if (structureDefinitionFile != null && mappingsDir != null) {
                if (!structureDefinitionFile.exists()) {
                    initialize = true;
                    structureDefinitionFile.createNewFile();
                }
                if (!mappingsDir.exists()) {
                    initialize = true;
                    mappingsDir.mkdirs();
                }
                this.canAccessDisc = structureDefinitionFile.isFile() && structureDefinitionFile.canRead() &&
                        structureDefinitionFile.canWrite() && mappingsDir.isDirectory() &&
                        mappingsDir.canWrite() && mappingsDir.canRead();

                if (canAccessDisc) {
                    logger.info("Terminology service accessing disk: storing mappings at " +
                            mappingsDir.getAbsolutePath() + " and storing structure definitions in " + structureDefinitionFile.getAbsolutePath());
                } else {
                    logger.info("Terminology service cannot access disk, changes will be transient.");
                }
            } else {
                this.canAccessDisc = false;
                logger.info("Terminology service cannot access disk, changes will be transient .");
            }
            if (initialize & canAccessDisc) {
                copyDefaultResourcesToDisk();
            }

        } catch (Exception e) {
            logger.warn("Error initializing MappingStore", e);
            canAccessDisc = false;
        }

        if (this.canAccessDisc) {
            // pull the resources currently saved to mappings dir
            assert mappingsDir != null;
            File[] mappingFiles = mappingsDir.listFiles();
            assert mappingFiles != null;
            for (File mappingFile : mappingFiles) {
                try {
                    savedMappings.put(mappingFile.getName(), IOUtils.toString(new FileInputStream(mappingFile), Charset.defaultCharset()));
                } catch (IOException e) {
                    logger.warn("Could not read the FHIR mapping resource: " + mappingFile.getName(), e);
                }
            }
            // add structureDefinitions from file into map.
            try {
                assert structureDefinitionFile != null;
                initializeStructureDefinition(new FileInputStream(structureDefinitionFile));
            } catch (IOException e) {
                logger.warn("Could not read the structure definition file. The Terminology Service will not be functional", e);
            }
        } else {
            // pull default resources
            for(String fileName : DEFAULT_MAPPING_RESOURCES) {
                InputStream configInputStream = this.getClass().getResourceAsStream(MAPPINGS_DIRECTORY + fileName);
                try {
                    assert configInputStream != null;
                    savedMappings.put(fileName, IOUtils.toString(configInputStream, Charset.defaultCharset()));
                } catch (IOException e) {
                    logger.warn("Could not read default FHIR mapping resource: " + fileName, e);
                }
            }
            // add default structureDefinition map
            try {
                initializeStructureDefinition(defaultSDFile);
            } catch (IOException e) {
                logger.warn("Error initializing structure definitions.", e);
            }
        }
        logger.info("MappingStore Initialized");
    }

    /**
     * Copies mapping resources and the structure definition file from the /resource directory into the persistent
     * volume, if the service can read/write to disk.
     * @throws IOException if it cannot read the default resources or write to disk.
     */
    public void copyDefaultResourcesToDisk() throws IOException {
        if (canAccessDisc) {
            for (String fileName : DEFAULT_MAPPING_RESOURCES) {
                InputStream configInputStream = this.getClass().getResourceAsStream(MAPPINGS_DIRECTORY + fileName);
                try {
                    assert configInputStream != null;
                    String mapping = IOUtils.toString(configInputStream, Charset.defaultCharset());
                    saveMapping(fileName, mapping);
                } catch (IOException e) {
                    logger.warn("Error saving default FHIR mapping resource to disk: " + fileName, e);
                    throw e;
                }
            }
            try {
                Files.copy(defaultSDFile, structureDefinitionFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                initializeStructureDefinition(new FileInputStream(structureDefinitionFile));
            } catch (IOException e) {
                logger.warn("Could not copy default structure definition file, the terminology service will not work", e);
                throw e;
            }
        }
    }

    /**
     * Saves a mapping with the given name to persistent storage if this MappingStore can read/write to disk then saves
     * a copy in memory.  If this MappingStore cannot read/write to disk, just stores the mapping in memory.
     * @param mappingName The name identifying the mapping to be saved.
     * @param mapping The json string for the mapping to be saved.
     * @throws IOException if the mapping JSON cannot be parsed, or if this MappingStore tries and fails to write to disk.
     */
    public void saveMapping(String mappingName, String mapping) throws IOException {
        if (canAccessDisc) {
            JsonNode jsonNode;
            File mappingFile = new File(mappingsDir + "/" + mappingName);
            try (BufferedWriter out = new BufferedWriter(new FileWriter(mappingFile, false))){
                jsonNode = jsonDeserializer.readTree(mapping);
                out.write(jsonNode.toPrettyString());
            } catch (IOException e) {
                logger.warn("Error parsing and saving mapping \"" + mappingName + "\" to disk.", e);
                throw e;
            }
        }
        savedMappings.put(mappingName, mapping);
    }

    /**
     * If the mapping with the name provided exists, this function deletes it from memory, and, if the MappingStore can
     * read/write to disk, from the mappings directory on the persistent volume.
     * @param mappingName The name of the mapping to be deleted.
     */
    public void deleteMapping(String mappingName) {
        if (canAccessDisc) {
            File mappingFile = new File(mappingsDir + "/" + mappingName);
            if (mappingExists(mappingName) && mappingFile.exists()) {
                boolean deleted = mappingFile.delete();
                if (deleted) {
                    logger.info("Mapping file " + mappingName + " deleted");
                    savedMappings.remove(mappingName);
                } else {
                    logger.warn("Error deleting mapping " + mappingName + ".");
                }
            }
        } else {
            savedMappings.remove(mappingName);
        }
    }

    /**
     * Checks whether a mapping with the given mappingName exists in memory
     * @param mappingName name of the mapping queried.
     * @return whether a mapping with the given mappingName exists in memory.
     */
    public boolean mappingExists(String mappingName) {
        return savedMappings.containsKey(mappingName);
    }

    /**
     * Gets the mapping associated with the given mappingName, or null if it doesn't exist.
     * @param mappingName name of the mapping queried.
     * @return The jsonstring mapping corresponding to the given mappingName in memory, or null if it doesn't exist.
     */
    public String getMapping(String mappingName) {
        return savedMappings.get(mappingName);
    }

    /**
     * Gets the map of saved resources
     * @return the saved resources mapping containing mappingNames and their corresponding json string mappings.
     */
    public Map<String, String> getSavedMappings() {
        return savedMappings;
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
    public void addSDMapping(String sdUri, String vsUri) throws IOException {

        structureDefinitions.put(sdUri, vsUri);
        boolean duplicate = containsSDMapping(sdUri, vsUri);
        if (canAccessDisc) {
            if (!duplicate) {
                try (BufferedWriter out = new BufferedWriter(new FileWriter(structureDefinitionFile, true))) {
                    out.write("\n" + sdUri + " <=> " + vsUri);
                } catch (IOException e) {
                    logger.warn("Error writing to structure definition file.", e);
                    throw e;
                }
            }
        }
    }

    /**
     * Checks whether a structure definition mapping exists between the given URI's on memory and, if the MappingStore
     * can access the disk, in the structureDefinition file on the persistent volume.
     * @param sdUri Structure definition URI
     * @param vsUri Value Set URI
     * @return whether or not the give SD Mapping exists already in this MappingStore
     * @throws IOException if the MappingStore tries and fails to read the structureDefinition file on disk.
     */
    public boolean containsSDMapping(String sdUri, String vsUri) throws IOException {
        boolean existsOnDisk = false;
        if (canAccessDisc) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(structureDefinitionFile), StandardCharsets.UTF_8))) {
                for (String line : reader.lines().collect(Collectors.toList())) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) {
                        continue;
                    }
                    String[] structureDefinitionToValueSet = line.split("<=>");
                    if (structureDefinitionToValueSet.length != 2) {
                        logger.warn("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    }
                    if (structureDefinitionToValueSet[0].trim().equals(sdUri) && structureDefinitionToValueSet[1].trim().equals(vsUri)) {
                        existsOnDisk = true;
                        break;
                    }
                }

            } catch (IOException e) {
                logger.warn("Could not read StructuredDefinition to ValueSet configuration mapping file: the Terminology Service won't be functional.", e);
                throw e;
            }
            return structureDefinitions.containsKey(sdUri) && structureDefinitions.get(sdUri).equals(vsUri) && existsOnDisk;
        } else {
            return structureDefinitions.containsKey(sdUri) && structureDefinitions.get(sdUri).equals(vsUri);
        }
    }

    /**
     * If this MappingStore can access the disk, this function searches the stored structureDefinition file for the line
     * containing the given Structure Definition Mapping, then deletes it before also deleting it from memory.
     * (probably not the best way to do this, as it pulls all the lines, deletes the selected one, then overwrites the
     * old file with a new one containing all but the deleted line).
     * @param sdUri Structure definition URI
     * @param vsUri Value Set URI
     * @throws IOException if the MappingStore tries and fails to read from or write to the structureDefinition file on
     *              disk.
     */
    public void deleteSDMapping(String sdUri, String vsUri) throws IOException {
        if (containsSDMapping(sdUri,vsUri)) {
            structureDefinitions.remove(sdUri);
            if (canAccessDisc) {
                List<String> lines;
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(structureDefinitionFile), StandardCharsets.UTF_8))) {
                    lines = reader.lines().collect(Collectors.toList());
                } catch (IOException e) {
                    logger.warn("Could not read StructuredDefinition to ValueSet configuration mapping file: the Terminology Service won't be functional.", e);
                    throw e;
                }
                String lineToDelete = null;
                for (String line: lines) {
                    String lineCopy = line.trim();
                    if (lineCopy.startsWith("#") || lineCopy.isEmpty()) {
                        continue;
                    }
                    String[] structureDefinitionToValueSet = lineCopy.split("<=>");
                    if (structureDefinitionToValueSet.length != 2) {
                        logger.warn("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    } else if (structureDefinitionToValueSet[0].trim().equals(sdUri) && structureDefinitionToValueSet[1].trim().equals(vsUri)) {
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
                        logger.warn("Error writing to Structure Definition File.", e);
                        throw e;
                    }
                }
            }
        }
    }

    /**
     * Gets all the structure definitions currently stored in memory.
     * @return all structure definitions from memory.
     */
    public Set<String> getAllStructureDefinitions() {
        HashSet<String> output = new HashSet<>();
        for (String left : structureDefinitions.keySet()) {
            String right = structureDefinitions.get(left);
            output.add(left + " <=> " + right);
        }
        return output;

    }

    /**
     * pulls the mappings from the given structure definition input stream into the valueSetMapping map.
     * @param mappingInputStream the inputStream to pull definitions from.  If this MappingStore is operating without
     *                           access to the disc, this will be used to pull from the default sd file from resources.
     *                           Otherwise, will be used to pull from the structureDefintion file stored on disc.
     * @throws IOException if the given inputStream cannot be accessed.
     */
    public void initializeStructureDefinition(InputStream mappingInputStream) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(mappingInputStream, StandardCharsets.UTF_8))) {
            reader.lines().forEach(line -> {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    return;
                }
                String[] structureDefinitionToValueSet = line.split("<=>");
                if (structureDefinitionToValueSet.length != 2) {
                    logger.info("Incorrect mapping found in structure definition needs to be {structure definition url} <=> {value set url}, but was " + line);
                    return;
                }
                try {
                    addSDMapping(structureDefinitionToValueSet[0].trim(), structureDefinitionToValueSet[1].trim());
                } catch (IOException e) {
                    logger.warn("Error writing to Structure Definition file while initializing.", e);
                }
            });
        } catch (IOException e) {
            logger.warn("Error reading from default structure definition file while initializing.", e);
            throw e;
        }
    }

    /**
     * Gets the map containing the structure definitions stored on disc.  Might need a better name.
     * @return the structure definitions map.
     */
    public BiMap<String, String> getStructureDefinitions() {
        return structureDefinitions;
    }

    /**
     * accessor for canAccessDisc
     * @return whether this MappingStore can access the disc.
     */
    public boolean getCanAccessDisc() {
        return canAccessDisc;
    }
}
