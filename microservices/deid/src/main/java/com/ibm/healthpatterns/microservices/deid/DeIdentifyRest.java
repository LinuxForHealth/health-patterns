package com.ibm.healthpatterns.microservices.deid;

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

@Path("/")
public class DeIdentifyRest {


	/**
	 * The file that contains the masking config that will be used to configure the de-id service.
	 */
	private static final String DEID_DEFAULT_CONFIG_JSON = "/de-id-config.json";
	private static final String DEID_DEFAULT_CONFIG_NAME = "default";
	private static final String DEID_CONFIG_PATH = "/mnt/data/";

	private static final String TRUE_STRING = "true";
	private static final String FALSE_STRING = "false";

	@ConfigProperty(name = "DEID_SERVICE_URL")
	String DEID_SERVICE_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_URL")
	String DEID_FHIR_SERVER_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_USERNAME")
	String DEID_FHIR_SERVER_USERNAME;

    @ConfigProperty(name = "DEID_FHIR_SERVER_PASSWORD")
	String DEID_FHIR_SERVER_PASSWORD;

	private DeIdentifier deid = null;
    private final ObjectMapper jsonDeserializer;


    private String configJson;
    private String defaultConfigJson;

    public DeIdentifyRest() {

        jsonDeserializer = new ObjectMapper();
        File defaultConfig = new File(DEID_CONFIG_PATH + DEID_DEFAULT_CONFIG_NAME);

        try {
            if (defaultConfig.createNewFile()) {
                BufferedWriter out = new BufferedWriter(new FileWriter(defaultConfig));
                out.write(configJson);
                out.close();
            }

            defaultConfigJson = getDefaultConfig();
        } catch (IOException e) {
            System.err.println("Could not read default de-identifier service configuration, the DeIdentifier won't be" +
                    "functional if a different configuration is not set.");
        }
    }

    private void initializeDeid() throws Exception {
        if (deid == null) {
            if (DEID_SERVICE_URL == null) {
                throw new Exception("DEID service URL not set");
            }
            if (DEID_FHIR_SERVER_URL == null ||
                DEID_FHIR_SERVER_USERNAME == null ||
                DEID_FHIR_SERVER_PASSWORD == null
            ) {
                throw new Exception("FHIR server URL/credentials not set");
            }
            deid = new DeIdentifier(DEID_SERVICE_URL, DEID_FHIR_SERVER_URL, DEID_FHIR_SERVER_USERNAME, DEID_FHIR_SERVER_PASSWORD, getDefaultConfig());
        }
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response deidentify(
            @QueryParam("configName") @DefaultValue(DEID_DEFAULT_CONFIG_NAME) String configName,
            @QueryParam("pushToFHIR") @DefaultValue(TRUE_STRING) String pushToFHIR,
            InputStream resourceInputStream
    ) {
        boolean boolPush;
        if (pushToFHIR.equalsIgnoreCase(TRUE_STRING)) {
            boolPush = true;
        } else if (pushToFHIR.equalsIgnoreCase(FALSE_STRING)) {
            boolPush = false;
        } else {
            return Response.status(400, "Bad value for parameter \"pushToFHIR\"").build();
        }
        File configFile = new File(DEID_CONFIG_PATH + configName);

        try {
            initializeDeid();
        } catch (Exception e) {
            return Response.status(500, e.toString()).build(); // Internal server error
        }
        if (!configFile.exists() && !configName.equals(DEID_DEFAULT_CONFIG_NAME)) {
            return Response.status(400, "No config with the identifier \"" + configName + "\" exists.").build();
        } else {
            String configString;
            if (configName.equals(DEID_DEFAULT_CONFIG_NAME)) {
                configString = defaultConfigJson;
            } else {
                try {
                    configString = Files.readString(java.nio.file.Path.of(DEID_CONFIG_PATH + configName));
                } catch (IOException e) {
                    return Response.status(500, e.toString()).build();
                }
            }

            deid.setConfigJson(configString);
        }

        try {
            DeIdentification result = deid.deIdentify(resourceInputStream, boolPush);
            return Response.ok(result.getDeIdentifiedResource().toPrettyString()).build();
        } catch (Exception e) {
            return Response.status(400, e.getMessage()).build(); // Bad request error
        }
    }

    @POST
    @Path("config")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response setConfig(InputStream resourceInputStream, @QueryParam("identifier") String name) throws Exception {
        if (name == null || name.isEmpty()) {
            return Response.status(400,  "Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter").build();
        }
        JsonNode jsonNode;
        try {
            jsonNode = jsonDeserializer.readTree(resourceInputStream);
        } catch (IOException e) {
            return Response.status(400,  "The given input stream did not contain valid JSON: "+ e).build();
        }
        File configFile = new File(DEID_CONFIG_PATH + name);
        if (!configFile.exists()) {
            BufferedWriter out = new BufferedWriter(new FileWriter(configFile));
            out.write(jsonNode.toPrettyString());
            out.close();
        } else {
            return Response.status(400, "Config with the identifier \"" + name + "\" already exists.").build();
        }

        return Response.ok().build();
    }

    @PUT
    @Path("config")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response putConfig(InputStream resourceInputStream, @QueryParam("identifier") String name) throws Exception {
        if (name == null || name.isEmpty()) {
            return Response.status(400,  "Config not given an identifier." +
                    "Specify an identifier for the config using the \"identifier\" query parameter").build();
        }
        JsonNode jsonNode;
        try {
            jsonNode = jsonDeserializer.readTree(resourceInputStream);
        } catch (IOException e) {
            return Response.status(400,  "The given input stream did not contain valid JSON: "+ e).build();
        }
        File configFile = new File(DEID_CONFIG_PATH + name);
        BufferedWriter out = new BufferedWriter(new FileWriter(configFile, false));
        out.write(jsonNode.toPrettyString());
        out.close();

        return Response.ok().build();
    }

    @GET
    @Path("config")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllConfigs() {
        File configPath = new File(DEID_CONFIG_PATH);
        File[] files = configPath.listFiles();
        StringBuilder out = new StringBuilder();
        assert files != null;
        for (File file : files) {
            out.append(file.getName()).append("\n");
        }
        return Response.ok(out.toString()).build();
    }

    @GET
    @Path("config/{configName}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response getConfig(@PathParam("configName") String configName) throws Exception {
        String configPath = DEID_CONFIG_PATH + configName;

        File configFile = new File(configPath);
        if (configFile.exists()) {
            return Response.ok(Files.readString(java.nio.file.Path.of(configPath))).build();
        } else {
            return Response.status(400, "No config with the identifier \"" + configName + "\" exists.").build();
        }
    }

    private String getDefaultConfig() throws IOException {
        InputStream configInputStream = this.getClass().getResourceAsStream(DEID_DEFAULT_CONFIG_JSON);

        assert configInputStream != null;
        configJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
        return configJson;
    }

    @GET
    @Path("healthCheck")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHealthCheck() {
        try {
            initializeDeid();
        } catch (Exception e) {
            return Response.status(500, e.toString()).build(); // Internal server error
        }

        StringWriter status = new StringWriter();
        if (deid.healthCheck(status)) {
            return Response.status(200).build(); // OK
        } else {
            return Response.status(500, status.toString()).build(); // Internal server error
        }
    }

}