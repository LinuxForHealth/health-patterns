package com.ibm.healthpatterns.deid;

import java.io.InputStream;

import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.core.MediaType;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;


@Path("/")
public class DeIdentifyRest {

    private ObjectMapper jsonDeserializer = new ObjectMapper();

    // config params as optional url parameters?

    // "database" of deid configs, select config via url param, if not use default.

    @POST
    @Path("deidentifyFHIR")
    @Consumes(MediaType.APPLICATION_JSON)
    public String deidentifyFHIR(InputStream resourceInputStream) throws Exception {
        JsonNode jsonNode;
		try {
			jsonNode = jsonDeserializer.readTree(resourceInputStream);
		} catch (JsonParseException e) {
			throw new Exception("The given input stream did not contain valid JSON.", e);
		}
		if (!(jsonNode instanceof ObjectNode)) {
			throw new Exception("The FHIR resource did not contain a valid JSON object, likely it was a JSON array. Currently only proper FHIR resources are supported");
		}
        return jsonNode.toPrettyString();

		/*
		DeIdentifier deid = new DeIdentifier(default values)
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
    public void setConfig() {

    }

}