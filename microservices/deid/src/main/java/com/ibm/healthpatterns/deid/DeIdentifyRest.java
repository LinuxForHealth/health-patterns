package com.ibm.healthpatterns.deid;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;


import org.apache.commons.io.IOUtils;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import org.jboss.resteasy.annotations.jaxrs.PathParam;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import com.ibm.healthpatterns.deid.*;

@Path("/")
public class DeIdentifyRest {


	/**
	 * The file that contains the masking config that will be used to configure the de-id service.
	 */
	private static final String DEID_CONFIG_JSON = "/de-id-config.json";

	private static final String DEID_SERVICE_URL = "http://ingestion-deid:8080/api/v1";
	private static final String DEID_FHIR_SERVER_URL = "http://ingestion-fhir-deid/fhir-server/api/v4";
	private static final String DEID_FHIR_SERVER_USEERNAME = "fhiruser";
	private static final String DEID_FHIR_SERVER_PASSWORD = "integrati0n";

    private ObjectMapper jsonDeserializer;
    
    private HashMap<String, String> configs;

    private String configJson;

    public DeIdentifyRest() {
        jsonDeserializer = new ObjectMapper();
        configs = new HashMap<String, String>();

		InputStream configInputStream = this.getClass().getResourceAsStream(DEID_CONFIG_JSON);
		try {
			configJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read default de-identifier service configuration, the DeIdentifier won't be" +
                    "functional if a different configuration is not set.");
		}
        
        configs.put("default", configJson);
    }

    // config params as optional url parameters?

    // "database" of deid configs, select config via url param, if not use default.

    @POST
    @Path("deidentifyFHIR")
    @Consumes(MediaType.APPLICATION_JSON)
    public String deidentifyFHIR(
            @HeaderParam("deid_service") @DefaultValue(DEID_SERVICE_URL) String deid_service,
            @HeaderParam("deid_server") @DefaultValue(DEID_FHIR_SERVER_URL) String deid_server,
            @HeaderParam("username") @DefaultValue(DEID_FHIR_SERVER_USEERNAME) String username,
            @HeaderParam("password") @DefaultValue(DEID_FHIR_SERVER_PASSWORD) String password,
            InputStream resourceInputStream
    ) {
        /*DeIdentifier deid = new DeIdentifier(deid_service, deid_server, username, password);
        try {
            DeIdentification result = deid.deIdentify(resourceInputStream);
            return result.getDeIdentifiedResource().toPrettyString();
        } catch (Exception e) {
            return e.toString();
        }*/
        try {
            return jsonDeserializer.readTree(this.getClass().getResourceAsStream(DEID_CONFIG_JSON)).toPrettyString();
        } catch (IOException e) {
            return e.toString();
        }
    public String deidentifyFHIR(InputStream resourceInputStream,
                                 @DefaultValue("default")
                                 @QueryParam("configName")
                                         String configName) throws Exception {
        JsonNode jsonNode;
        String configString = configs.get(configName);
		try {
			jsonNode = jsonDeserializer.readTree(resourceInputStream);
		} catch (JsonParseException e) {
			throw new Exception("The given input stream did not contain valid JSON.", e);
		}
		if (!(jsonNode instanceof ObjectNode)) {
			throw new Exception("The FHIR resource did not contain a valid JSON object, likely it was a JSON array. Currently only proper FHIR resources are supported");
		}
        return jsonNode.toPrettyString();


		//DeIdentifier deid = new DeIdentifier(null, null, null, null);

		//deid.setConfigJson(configString);
		/*
		deidentified = deid.deIdentify(InputStream)
		return deidentified.getDeIdentifiedResource()
		 */
    }

    @POST
    @Path("deidentify")
    @Consumes(MediaType.APPLICATION_JSON)
    public String deidentify() {
        return null;
    }

    @POST
    @Path("postdeidconfig")
    @Consumes(MediaType.APPLICATION_JSON)
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

}