package com.ibm.healthpatterns.microservices.deid;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.nio.charset.Charset;
import java.util.HashMap;


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

	@ConfigProperty(name = "DEID_SERVICE_URL")
	String DEID_SERVICE_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_URL")
	String DEID_FHIR_SERVER_URL;

    @ConfigProperty(name = "DEID_FHIR_SERVER_USERNAME")
	String DEID_FHIR_SERVER_USERNAME;

    @ConfigProperty(name = "DEID_FHIR_SERVER_PASSWORD")
	String DEID_FHIR_SERVER_PASSWORD;

	private DeIdentifier deid = null;
    private ObjectMapper jsonDeserializer;
    
    private HashMap<String, String> configs;

    private String defaultConfigJson;

    public DeIdentifyRest() {

        jsonDeserializer = new ObjectMapper();
        configs = new HashMap<String, String>();

		InputStream configInputStream = this.getClass().getResourceAsStream(DEID_DEFAULT_CONFIG_JSON);
		try {
			defaultConfigJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read default de-identifier service configuration, the DeIdentifier won't be" +
                    "functional if a different configuration is not set.");
		}
        
        configs.put("default", defaultConfigJson);
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
            deid = new DeIdentifier(DEID_SERVICE_URL, DEID_FHIR_SERVER_URL, DEID_FHIR_SERVER_USERNAME, DEID_FHIR_SERVER_PASSWORD, defaultConfigJson);
        }
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response deidentify(
            @QueryParam("configName") @DefaultValue(DEID_DEFAULT_CONFIG_NAME) String configName,
            @QueryParam("pushToFHIR") @DefaultValue("true") String pushToFHIR,
            InputStream resourceInputStream
    ) {
        boolean boolPush = pushToFHIR.equals("true");
        try {
            initializeDeid();
        } catch (Exception e) {
            return Response.status(500, e.toString()).build(); // Internal server error
        }

        try {
            if (!configs.containsKey(configName)) {
                throw new Exception();
            }
            String configString = configs.get(configName);
            deid.setConfigJson(configString);
            DeIdentification result = deid.deIdentify(resourceInputStream, boolPush);
            return Response.status(200, result.getDeIdentifiedResource().toPrettyString()).build(); // OK
        } catch (Exception e) {
            return Response.status(400).build(); // Bad request error
        }
    }

    @POST
    @Path("config")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public String setConfig(InputStream resourceInputStream, @QueryParam("identifier") String name) throws Exception {
        if (name == null || name.isEmpty()) throw new Exception("Config not given an identifier." +
                "Specify an identifier for the config using the \"identifier\" query parameter");
        JsonNode jsonNode;
        try {
            jsonNode = jsonDeserializer.readTree(resourceInputStream);
        } catch (IOException e) {
            throw new Exception("The given input stream did not contain valid JSON.", e);
        }
        configs.put(name, jsonNode.toString());
        return "New configuration stored with the identifier \"" + name +
                "\".  Apply the config by setting the query parameter \"configName\" equal to the config's identifier.";
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