package com.ibm.healthpatterns.microservices.terminology;

import java.io.*;
import java.nio.charset.StandardCharsets;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.IOUtils;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import org.jboss.logging.Logger;

@Path("/")
public class TerminologyRest {

    @ConfigProperty(name = "FHIR_SERVER_URL")
    String FHIR_SERVER_URL;

    @ConfigProperty(name = "FHIR_SERVER_USERNAME")
    String FHIR_SERVER_USERNAME;

    @ConfigProperty(name = "FHIR_SERVER_PASSWORD")
    String FHIR_SERVER_PASSWORD;

    @ConfigProperty(name = "PV_PATH", defaultValue ="")
    String PV_PATH;

    private TerminologyService terminologyService = null;

    private static final Logger logger = Logger.getLogger(TerminologyRest.class);

    private MappingStore mappingStore = null;

    /**
     * Used as a pseudo-constructor, as the constructor runs before the @ConfigProperties are injected.
     * Initializes the mappingStore and terminologyService, should be invoked at the start of any rest function that
     * needs to use either.
     * @throws Exception if the FHIR credentials are not set.
     */
    private void initializeService() throws Exception {
        if (mappingStore == null) {
            logger.info("initializing MappingStore...");
            if (PV_PATH.isBlank()) {
                mappingStore = new MappingStore(null, null);
            } else {
                if (!PV_PATH.endsWith("/")) PV_PATH = PV_PATH + "/";
                File mappingsDirFile = new File(PV_PATH + "mappings");
                File structureDefinitionFile = new File(PV_PATH + "structureDefinition.mappings");
                mappingStore = new MappingStore(structureDefinitionFile, mappingsDirFile);
            }

        }
        if (terminologyService == null) {

            if (FHIR_SERVER_URL == null ||
                FHIR_SERVER_USERNAME == null ||
                FHIR_SERVER_PASSWORD == null
            ) {
                throw new Exception("FHIR server URL/credentials not set");
            }
            terminologyService = new TerminologyService(FHIR_SERVER_URL, FHIR_SERVER_USERNAME, FHIR_SERVER_PASSWORD, mappingStore);
        }
    }

    /**
     * Translates the provided FHIR resource using the structure definitions and mappings stored in the MappingStore and
     * installed on the FHIR server.
     * @param resourceInputStream the FHIR bundle to be translated.
     * @return HTTP Response containing the result of the translation, or an error status.
     */
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Object translate(InputStream resourceInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }

        try {
            Translation result = terminologyService.translate(resourceInputStream);
            logger.info("Resource translation successful");
            return result.getTranslatedResource().toPrettyString();
        } catch (Exception e) {
            logger.warn(e);
            return Response.status(400).entity("Request could not be processed with given data.").build(); // Bad request error
        }
    }

    /**
     * Healthcheck for the API - checks to see that the initialization is successful and the necessary services are up.
     * @return a 200 HTTP response if the initialization runs cleanly and the terminology service is up, 500 otherwise.
     */
    @GET
    @Path("healthCheck")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHealthCheck() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }

        StringWriter status = new StringWriter();
        if (terminologyService.healthCheck(status)) {
            logger.info("Terminology microservice is functional");
            return Response.status(200).build(); // OK
        } else {
            logger.warn(status.toString());
            return Response.status(500).entity(status.toString()).build(); // Internal server error
        }
    }

    /**
     * Posts a ValueSet translation mapping to the MappingStore with the given name, then installs it on the FHIR
     * server.  Does not overwrite a preexisting mapping with the same name.
     * @param resourceInputStream Body of the request, the ValueSet mapping as JSON
     * @param name the identifier with which to associate the ValueSet mapping.
     * @return HTTP Response containing whether the post was successful, or an error status.
     */
    @POST
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response postMapping(InputStream resourceInputStream, @PathParam("mappingName") String name) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        if (name == null || name.isEmpty()) {
            logger.warn("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"identifier\" query parameter");
            return Response.status(400).entity("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"identifier\" query parameter").build();
        }
        String resourceString;
        if (!mappingStore.mappingExists(name)) {
            try {
                resourceString = IOUtils.toString(resourceInputStream, StandardCharsets.UTF_8);
                mappingStore.saveMapping(name, resourceString);
            } catch (IOException e) {
                logger.warn("Error parsing and saving mapping: ", e);
                return Response.status(500).entity("Error parsing and saving mapping: " + e).build();
            }
            boolean installed = terminologyService.installTranslationResource(name, resourceString);
            if (!installed) {
                logger.warn("Error installing FHIR Resource \"" + name + "\".  Translation might not work.");
                return Response.status(500).entity("Error installing FHIR Resource \"" + name + "\".  Translation might not work.").build();
            }
        } else {
            logger.warn("Mapping with the identifier \"" + name + "\" already exists.");
            return Response.status(400).entity("Mapping with the identifier \"" + name + "\" already exists.").build();
        }
        logger.info("Mapping Resource \"" + name + "\" created:\n" + resourceString);
        return Response.ok("Mapping Resource \"" + name + "\" created:\n" + resourceString).build();
    }

    /**
     * PUTs a ValueSet translation mapping to the MappingStore with the given name, then installs it on the FHIR server.
     * @param resourceInputStream Body of the request, the ValueSet mapping as JSON
     * @param name the identifier with which to associate the ValueSet mapping.
     * @return HTTP Response containing whether the post was successful, or an error status.
     */
    @PUT
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response putMapping(InputStream resourceInputStream, @PathParam("mappingName") String name) throws Exception {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        if (name == null || name.isEmpty()) {
            logger.warn("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"mappingName\" path parameter");
            return Response.status(400).entity("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"mappingName\" path parameter").build();
        }
        boolean exists = mappingStore.mappingExists(name);
        String resourceString = IOUtils.toString(resourceInputStream, StandardCharsets.UTF_8);
        mappingStore.saveMapping(name, resourceString);
        boolean installed = terminologyService.installTranslationResource(name, resourceString);
        if (!installed) {
            logger.warn("Error installing FHIR Resource \"" + name + "\".  Translation might not work.");
            return Response.status(500).entity("Error installing FHIR Resource \"" + name + "\".  Translation might not work.").build();
        }
        if (exists) {
            logger.info("Mapping Resource \"" + name + "\" updated:\n" + resourceString);
            return Response.ok("Mapping Resource \"" + name + "\" updated:\n" + resourceString).build();
        }
        return Response.ok("Mapping Resource \"" + name + "\" created:\n" + resourceString).build();
    }

    /**
     * Gets a list of the names of all mappings saved to the MappingStore which are installed on the FHIR server.
     * @return a failure response or a success response containing a list of the mappings saved
     * to the MappingStore.  Does not include mappings installed on the FHIR server that have been deleted from the
     * mapping store.
     */
    @GET
    @Path("mapping")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllMappings() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        StringBuilder out = new StringBuilder();
        for (String mappingName : mappingStore.getSavedMappings().keySet()) {
            out.append(mappingName).append("\n");
        }
        logger.info("Returned mappings");
        return Response.ok(out.toString()).build();
    }

    /**
     * Gets the mapping identified with the given mapping.
     * @param mappingName the name of the mapping to retrieve.
     * @return HTTP response indicating success or failure, success containing the mapping's json in its body.
     */
    @GET
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getMapping(@PathParam("mappingName") String mappingName) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        if (mappingStore.mappingExists(mappingName)) {
            logger.info("Returned mapping \""+mappingName+"\"");
            return Response.ok(mappingStore.getMapping(mappingName)).build();
        } else {
            logger.warn("No mapping with the identifier \"" + mappingName + "\" exists.");
            return Response.status(400).entity("No mapping with the identifier \"" + mappingName + "\" exists.").build();
        }
    }

    /**
     * Deletes the specified mapping.  Does not uninstall the mapping from the FHIR server if it is already installed,
     * just prevents future deployments from attempting to install it.
     *
     * @param mappingName Path parameter, specifies which mapping file to return
     * @return HTTP Response with success or failure.
     */
    @DELETE
    @Path("mapping/{mappingName}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response deleteMapping(@PathParam("mappingName") String mappingName) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        if (mappingStore.mappingExists(mappingName)) {
            mappingStore.deleteMapping(mappingName);
            logger.info("Mapping file " + mappingName + " deleted");
            return Response.ok().entity("Mapping file " + mappingName + " deleted").build();
        } else {
            logger.warn("No mapping with the identifier \"" + mappingName + "\" exists.");
            return Response.status(400).entity("No mapping with the identifier \"" + mappingName + "\" exists.").build();
        }
    }

    /**
     * Saves a new structure definition.
     * @param sdInputStream body of the request, should be JSON of the following structure:
     *                      {
     *                          "sdUri" : "https://www.exampleURI.org/FHIR/SD/exampleStructureDefinition",
     *                          "vsUri" : "https://www.exampleURI.org/FHIR/VS/exampleValueSet"
     *                      }
     * @return response with success or failure
     */
    @POST
    @Path("structureDefinitions")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response postStructureDefinition(InputStream sdInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        ObjectMapper jsonDeserializer = new ObjectMapper();
        JsonNode jsonNode;
        String sdUri;
        String vsUri;
        try {
            jsonNode = jsonDeserializer.readTree(sdInputStream);
            if (jsonNode.get("sdUri") == null || jsonNode.get("vsUri") == null ) {
                logger.warn("Improperly formatted json request:  should contain the fields \"sdUri\" and \"vsUri\"");
                return Response.status(400).entity("Improperly formatted json request:  should contain the fields \"sdUri\" and \"vsUri\"").build();
            }
            sdUri = jsonNode.get("sdUri").asText();
            vsUri = jsonNode.get("vsUri").asText();
            mappingStore.addSDMapping(sdUri, vsUri);
            logger.info("Successfully added structure definition \""+vsUri+" <=> "+sdUri+"\"");
            return Response.ok("Successfully added structure definition \""+vsUri+" <=> "+sdUri+"\"").build();
        } catch (IOException e) {
            logger.warn("Error posting structure definiton: " + e);
            return Response.status(400).entity("Error posting structure definiton: " + e).build();
        }
    }

    /**
     * Gets all saved structureDefinitions.
     *
     * @return HTTP response with the saved structureDefinitions in the body, or a 500 response.
     */
    @GET
    @Path("structureDefinitions")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllStructureDefinitions() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        String[] definitions = mappingStore.getAllStructureDefinitions().toArray(new String[0]);
        StringBuilder out = new StringBuilder();
        for (String definition : definitions) {
            out.append(definition).append("\n");
        }
        logger.info("Returned structure definitions");
        return Response.ok(out.toString().trim()).build();
    }

    /**
     * Deletes the specified mapping.
     *
     * @return HTTP Response with success or failure.
     */
    @DELETE
    @Path("structureDefinitions")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response deleteStructureDefinition(InputStream sdInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e+"\"").build(); // Internal server error
        }
        ObjectMapper jsonDeserializer = new ObjectMapper();
        JsonNode jsonNode;
        String sdUri;
        String vsUri;
        try {
            jsonNode = jsonDeserializer.readTree(sdInputStream);
            sdUri = jsonNode.get("sdUri").asText();
            vsUri = jsonNode.get("vsUri").asText();
            if (sdUri.isEmpty() || vsUri.isEmpty()) {
                logger.warn("Improperly formatted json request:  should contain the fields \"sdUri\" and \"vsUri\"");
                return Response.status(400).entity("Improperly formatted json request:  should contain the fields \"sdUri\" and \"vsUri\"").build();
            }
        } catch (IOException e) {
            logger.warn("Bad JSON: " + e);
            return Response.status(400).entity("Bad JSON: " + e).build();
        }

        try {
            if (mappingStore.containsSDMapping(sdUri, vsUri)) {
                    mappingStore.deleteSDMapping(sdUri, vsUri);
                logger.info("Mapping " +sdUri + " <=> " + vsUri +" deleted");
                return Response.ok().entity("Mapping " +sdUri + " <=> " + vsUri +" deleted").build();
            } else {
                logger.warn("No mapping \"" +sdUri + " <=> " + vsUri +"\" exists");
                return Response.status(400).entity("No mapping \"" +sdUri + " <=> " + vsUri +"\" exists").build();
            }
        } catch (IOException e) {
            logger.warn("Error deleting Structure Definition mapping: ", e);
            return Response.status(400).entity("Error deleting Structure Definition mapping: " + e).build();
        }
    }
}
