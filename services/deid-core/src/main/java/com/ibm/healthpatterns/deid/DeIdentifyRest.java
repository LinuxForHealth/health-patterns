package com.ibm.healthpatterns.deid;

import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;

import org.apache.commons.io.IOUtils;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import org.jboss.logging.Logger;

@Path("/")
public class DeIdentifyRest {

	/**
	 * The file that contains the masking config that will be used to configure the de-id service.
	 */
	private static final String DEID_DEFAULT_CONFIG_JSON = "/de-id-config.json";
	private static final String DEID_DEFAULT_CONFIG_NAME = "default";

	@ConfigProperty(name = "DEID_SERVICE_URL")
	String DEID_SERVICE_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_URL")
	String DEID_FHIR_SERVER_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_USERNAME")
	String DEID_FHIR_SERVER_USERNAME;

    @ConfigProperty(name = "DEID_FHIR_SERVER_PASSWORD")
	String DEID_FHIR_SERVER_PASSWORD;

    @ConfigProperty(name = "PV_PATH")
    String PV_PATH = "/mnt/data/";


    private DeIdentifier deid = null;
    private final ObjectMapper jsonDeserializer;

    private static final Logger logger = Logger.getLogger(DeIdentifyRest.class);

    /*
    / Used if the persistent volume is not available
     */
    private String defaultConfigJson;

    public DeIdentifyRest() {

        jsonDeserializer = new ObjectMapper();
        File defaultConfig = new File(PV_PATH + DEID_DEFAULT_CONFIG_NAME);

        try {
            defaultConfigJson = getDefaultConfig();

            if (defaultConfig.createNewFile()) {
                BufferedWriter out = new BufferedWriter(new FileWriter(defaultConfig));
                out.write(defaultConfigJson);
                out.close();
            }
        } catch (IOException e) {
            logger.warn("Could not read default de-identifier service configuration, the DeIdentifier won't be" +
                    "functional if a different configuration is not set.");
        }
    }

    /**
     * Initializes the DeIdentifier, which connects to the FHIR server
     * @throws Exception If FHIR credentials are improperly initialized.
     */
    private void initializeDeid(String configString) throws Exception {
        if (DEID_SERVICE_URL == null) {
            throw new Exception("DEID service URL not set");
        }
        if (DEID_FHIR_SERVER_URL == null ||
            DEID_FHIR_SERVER_USERNAME == null ||
            DEID_FHIR_SERVER_PASSWORD == null
        ) {
            throw new Exception("FHIR server URL/credentials not set");
        }
        deid = DeIdentifier.getDeIdentifier(DEID_SERVICE_URL, DEID_FHIR_SERVER_URL, DEID_FHIR_SERVER_USERNAME,
                DEID_FHIR_SERVER_PASSWORD, configString);
    }

    /**
     * Passes the given FHIR Resource through the deidentification service, pushing to the FHIR server if the pushToFHIR
     * parameter is set to true.
     * @param configName Query parameter that tells which specific configuration file to use, if unspecified uses the
     *                   "default" configuration.
     * @param pushToFHIR Query parameter that tells whether or not to push the resulting deidentified resource to the
     *                   FHIR server, defaults to True
     * @param resourceInputStream Request body, the FHIR resource to be deidentified as a JSON object
     * @return Http response containing the deidentified resource if successful
     */
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response deidentify(
            @QueryParam("configName") @DefaultValue(DEID_DEFAULT_CONFIG_NAME) String configName,
            @QueryParam("pushToFHIR") @DefaultValue("true") Boolean pushToFHIR,
            InputStream resourceInputStream
    ) {
        File configFile = new File(PV_PATH + configName);

        if (!configFile.exists() && !configName.equals(DEID_DEFAULT_CONFIG_NAME)) {
            logger.warn("No config with the identifier \"" + configName + "\" exists.");
            return Response.status(400).entity("No config with the identifier \"" + configName + "\" exists.").build();
        }
        String configString;
        if (configName.equals(DEID_DEFAULT_CONFIG_NAME)) {
            configString = defaultConfigJson;
        } else {
            try {
                configString = Files.readString(java.nio.file.Path.of(PV_PATH + configName));
            } catch (IOException e) {
                logger.warn("The config \"" + configName + "\" should exist, but the file could not be found.");
                return Response.status(500).entity("The config \"" + configName + "\" should exist, but the file could not be found.").build();
            }
        }
        try {
            initializeDeid(configString);
        } catch (Exception e) {
            logger.warn("The Deidentifier could not be initialized");
            return Response.status(500).entity("The Deidentifier could not be initialized").build(); // Internal server error
        }

        try {
            DeIdentification result = deid.deIdentify(resourceInputStream, pushToFHIR);
            logger.info("Resource successfully deidentified");
            return Response.ok(result.getDeIdentifiedResource().toPrettyString()).build();
        } catch (Exception e) {
            logger.warn("Request could not be processed."+
                    "Either you posted invalid data, or we could not communicate with the deid service.");
            return Response.status(400).entity("Request could not be processed."+
                    "Either you posted invalid data, or we could not communicate with the deid service.").build(); // Bad request error
        }
    }

    /**
     * Method for posting configuration json files to the connected persistent volume, if there is one.
     * @param resourceInputStream Request body, the deidentification configuration as a JSON string.
     * @param name Query parameter specifying the identifier to save the file under.  If file already exists, returns
     *             a 400 error.
     * @return Http Response
     * @throws IOException if there is an error writing to the persistent volume
     */
    @POST
    @Path("config/{configName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response postConfig(InputStream resourceInputStream, @PathParam("configName") String name) throws IOException {
        if (name == null || name.isEmpty()) {
            logger.warn("Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter");
            return Response.status(400).entity("Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter").build();
        }
        JsonNode jsonNode;
        try {
            jsonNode = jsonDeserializer.readTree(resourceInputStream);
        } catch (IOException e) {
            logger.warn("The given input stream did not contain valid JSON: "+ e);
            return Response.status(400).entity("The given input stream did not contain valid JSON: "+ e).build();
        }
        File configFile = new File(PV_PATH + name);
        if (!configFile.exists()) {
            BufferedWriter out = new BufferedWriter(new FileWriter(configFile));
            out.write(jsonNode.toPrettyString());
            out.close();
        } else {
            logger.warn("Config with the identifier \"" + name + "\" already exists.");
            return Response.status(400).entity("Config with the identifier \"" + name + "\" already exists.").build();
        }
        logger.info("Config " + name + " added:\n");
        return Response.ok("Config " + name + " added:\n" + jsonNode.toPrettyString()).build();
    }

    /**
     * Method for putting configuration json files to the connected persistent volume, if there is one.
     *
     * @param resourceInputStream Request body, the deidentification configuration as a JSON string.
     * @param name Query parameter specifying the identifier to save the file under.  If file already exists, overwrites
     *             it with new JSON
     * @return Http Response
     * @throws IOException if there is an error writing to the persistent volume
     */
    @PUT
    @Path("config/{configName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response putConfig(InputStream resourceInputStream, @PathParam("configName") String name) throws Exception {
        if (name == null || name.isEmpty()) {
            logger.warn("Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter");
            return Response.status(400).entity("Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter").build();
        }
        JsonNode jsonNode;
        try {
            jsonNode = jsonDeserializer.readTree(resourceInputStream);
        } catch (IOException e) {
            logger.warn("The given input stream did not contain valid JSON: "+ e);
            return Response.status(400).entity("The given input stream did not contain valid JSON: "+ e).build();
        }
        File configFile = new File(PV_PATH + name);
        boolean update = configFile.exists();
        BufferedWriter out = new BufferedWriter(new FileWriter(configFile, false));
        out.write(jsonNode.toPrettyString());
        out.close();
        if (update) {
            logger.info("Config " + name + " updated.");
            return Response.ok("Config " + name + " updated to:\n" + jsonNode.toPrettyString()).build();
        }
        logger.info("Config " + name + " added.");
        return Response.ok("Config " + name + " added:\n" + jsonNode.toPrettyString()).build();
    }

    /**
     * Gets a list of all config files stored on the persistent volume
     * @return A string containing the filenames of the JSON configs.
     */
    @GET
    @Path("config")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllConfigs() {
        File configPath = new File(PV_PATH);
        File[] files = configPath.listFiles();
        StringBuilder out = new StringBuilder();
        assert files != null;
        for (File file : files) {
            out.append(file.getName()).append("\n");
        }
        logger.info("Config list displayed.");
        return Response.ok(out.toString()).build();
    }

    /**
     * Gets the content of the specified config file.
     *
     * @param configName Path parameter, specifies which configuration file to return
     * @return HTTP Response with a body containing JSON string contents of the config file specified, or a 400 if the
     *         file doesn't exist.
     * @throws IOException if there is an error reading the file
     */
    @GET
    @Path("config/{configName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getConfig(@PathParam("configName") String configName) throws IOException {
        String configPath = PV_PATH + configName;

        File configFile = new File(configPath);
        if (configFile.exists()) {
            logger.info("Config found.");
            return Response.ok(Files.readString(java.nio.file.Path.of(configPath))).build();
        } else {
            logger.warn("No config with the identifier \"" + configName + "\" exists.");
            return Response.status(400).entity("No config with the identifier \"" + configName + "\" exists.").build();
        }
    }

    /**
     * Deletes the content of the specified config file.
     *
     * @param configName Path parameter, specifies which configuration file to return
     * @return HTTP Response with success or failure.
     */
    @DELETE
    @Path("config/{configName}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response deleteConfig(@PathParam("configName") String configName) {
        String configPath = PV_PATH + configName;

        File configFile = new File(configPath);
        if (configFile.exists()) {
            boolean deleted = configFile.delete();
            if (deleted) {
                logger.info("Config file " + configName + " deleted");
                return Response.ok().entity("Config file " + configName + " deleted").build();
            } else {
                logger.warn("Error deleting config " + configName + ".");
                return Response.status(500).entity("Error deleting config " + configName + ".").build();
            }
        } else {
            logger.warn("No config with the identifier \"" + configName + "\" exists.");
            return Response.status(400).entity("No config with the identifier \"" + configName + "\" exists.").build();
        }
    }

    private String getDefaultConfig() throws IOException {
        InputStream configInputStream = this.getClass().getResourceAsStream(DEID_DEFAULT_CONFIG_JSON);
        assert configInputStream != null;
        return IOUtils.toString(configInputStream, Charset.defaultCharset());
    }

    /**
     * Health check for the REST api
     * @return HTTP response OK if the deidentification service is healthy, HTTP response 500 otherwise.
     */
    @GET
    @Path("healthCheck")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHealthCheck() {
        try {
            initializeDeid(defaultConfigJson);
        } catch (Exception e) {
            logger.warn("The Deidentifier could not be initialized.");
            return Response.status(500).entity("The Deidentifier could not be initialized.").build(); // Internal server error
        }

        StringWriter status = new StringWriter();
        if (deid.healthCheck(status)) {
            logger.info("Deidentification FHIR server had no errors");
            return Response.status(200).build(); // OK
        } else {
            logger.warn(status.toString());
            return Response.status(500).entity(status.toString()).build(); // Internal server error
        }
    }

}