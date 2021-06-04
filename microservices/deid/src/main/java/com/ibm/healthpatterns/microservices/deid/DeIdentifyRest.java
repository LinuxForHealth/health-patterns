package com.ibm.healthpatterns.microservices.deid;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.HashMap;


import org.apache.commons.io.IOUtils;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;

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

	private DeIdentifier DEID = null;
    private ObjectMapper jsonDeserializer;
    
    private HashMap<String, String> configs;

    private String configJson;

    public DeIdentifyRest() {

        jsonDeserializer = new ObjectMapper();
        configs = new HashMap<String, String>();

		InputStream configInputStream = this.getClass().getResourceAsStream(DEID_DEFAULT_CONFIG_JSON);
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
            @QueryParam("configName") @DefaultValue(DEID_DEFAULT_CONFIG_NAME) String configName,
            InputStream resourceInputStream
    ) {
        if (DEID == null){
            DEID = new DeIdentifier(DEID_SERVICE_URL, DEID_FHIR_SERVER_URL, DEID_FHIR_SERVER_USERNAME, DEID_FHIR_SERVER_PASSWORD);
        }


        String configString = configs.get(configName);
        DEID.setConfigJson(configString);

        try {
            DeIdentification result = DEID.deIdentify(resourceInputStream);
            return result.getDeIdentifiedResource().toPrettyString();
        } catch (Exception e) {
            return e.toString();
        }
        //return DEID_SERVICE_URL + '\n' + DEID_FHIR_SERVER_URL + '\n' + DEID_FHIR_SERVER_USERNAME + '\n' + DEID_FHIR_SERVER_PASSWORD;
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