package com.ibm.healthpatterns.microservices.terminology;

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
public class TerminologyRest {

    @ConfigProperty(name = "FHIR_SERVER_URL")
    String FHIR_SERVER_URL;

    @ConfigProperty(name = "FHIR_SERVER_USERNAME")
    String FHIR_SERVER_USERNAME;

    @ConfigProperty(name = "FHIR_SERVER_PASSWORD")
    String FHIR_SERVER_PASSWORD;

    private volatile TerminologyService terminologyService;

    public TerminologyRest() {

    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public String translate(InputStream resourceInputStream) {
        if (terminologyService == null) {
            terminologyService = new TerminologyService(FHIR_SERVER_URL, FHIR_SERVER_USERNAME, FHIR_SERVER_PASSWORD);
        }
        try {
            Translation result = terminologyService.translate(resourceInputStream);
            return result.getTranslatedResource().toPrettyString();
        } catch (Exception e) {
            return e.toString();
        }
    }

}
