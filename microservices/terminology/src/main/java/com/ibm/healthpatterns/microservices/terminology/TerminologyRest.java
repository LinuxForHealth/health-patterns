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

    @ConfigProperty(name = "PV_PATH")
    String PV_PATH;

    private TerminologyService terminologyService = null;

    private static final Logger logger = Logger.getLogger(TerminologyRest.class);

    private MappingStore mappingStore = null;

    private void initializeService() throws Exception {
        if (mappingStore == null) {
            File mappingsDirFile = new File(PV_PATH + "mappings/");
            File structureDefinitionFile = new File(PV_PATH + "structureDefinition.mappings");
            mappingStore = new MappingStore(structureDefinitionFile, mappingsDirFile);
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

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Object translate(InputStream resourceInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
        }

        try {
            Translation result = terminologyService.translate(resourceInputStream);
            logger.info("Resource translation successful");
            return result.getTranslatedResource().toPrettyString();
        } catch (Exception e) {
            logger.warn(e.toString());
            return Response.status(400).entity("Request could not be processed with given data.").build(); // Bad request error
        }
    }

    @GET
    @Path("healthCheck")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHealthCheck() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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

    @POST
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response postMapping(InputStream resourceInputStream, @PathParam("mappingName") String name) throws Exception {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
        }
        if (name == null || name.isEmpty()) {
            logger.warn("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"identifier\" query parameter");
            return Response.status(400).entity("Mapping not given an identifier." +
                    "Specify an identifier for the mapping using the \"identifier\" query parameter").build();
        }
        String resourceString;
        if (!mappingStore.mappingExists(name)) {
            resourceString = IOUtils.toString(resourceInputStream, StandardCharsets.UTF_8);
            mappingStore.saveMapping(name, resourceString);
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

    @PUT
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response putMapping(InputStream resourceInputStream, @PathParam("mappingName") String name) throws Exception {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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

    @GET
    @Path("mapping")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllMappings() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
        }
        StringBuilder out = new StringBuilder();
        for (String mappingName : mappingStore.getSavedResourcesMapping().keySet()) {
            out.append(mappingName).append("\n");
        }
        logger.info("Returned mappings");
        return Response.ok(out.toString()).build();
    }

    @GET
    @Path("mapping/{mappingName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getMapping(@PathParam("mappingName") String mappingName) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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
     * Deletes the speicied mapping.
     *
     * @param mappingName Path parameter, specifies which mappinguration file to return
     * @return HTTP Response with success or failure.
     */
    @DELETE
    @Path("mapping/{mappingName}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response deleteMapping(@PathParam("mappingName") String mappingName) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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

    @POST
    @Path("structureDefinitions")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response postStructureDefinition(InputStream sdInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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
        } catch (IOException e) {
            logger.warn("Bad JSON: " + e.toString());
            return Response.status(400).entity("Bad JSON: " + e.toString()).build();
        }
        mappingStore.addSDMapping(sdUri, vsUri);
        logger.info("Successfully added structure definition \""+vsUri+" <=> "+sdUri+"\"");
        return Response.ok().build();
    }

    @GET
    @Path("structureDefinitions")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllStructureDefinitions() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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
     * Deletes the speicied mapping.
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
            logger.warn("Could not initialize terminology service: \""+e.toString()+"\"");
            return Response.status(500).entity("Could not initialize terminology service: \""+e.toString()+"\"").build(); // Internal server error
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


        if (mappingStore.containsSDMapping(sdUri, vsUri)) {
            mappingStore.deleteSDMapping(sdUri, vsUri);
            logger.info("Mapping " +sdUri + " <=> " + vsUri +" deleted");
            return Response.ok().entity("Mapping " +sdUri + " <=> " + vsUri +" deleted").build();
        } else {
            logger.warn("No mapping \"" +sdUri + " <=> " + vsUri +"\" exists");
            return Response.status(400).entity("No mapping \"" +sdUri + " <=> " + vsUri +"\" exists").build();
        }
    }
}
