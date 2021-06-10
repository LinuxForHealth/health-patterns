package com.ibm.healthpatterns.microservices.terminology;

import java.io.InputStream;
import java.io.StringWriter;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

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

    private TerminologyService terminologyService = null;

    private static final Logger logger = Logger.getLogger(TerminologyRest.class);

    private void initializeService() throws Exception {
        if (terminologyService == null) {
            if (FHIR_SERVER_URL == null ||
                FHIR_SERVER_USERNAME == null ||
                FHIR_SERVER_PASSWORD == null
            ) {
                throw new Exception("FHIR server URL/credentials not set");
            }
            terminologyService = new TerminologyService(FHIR_SERVER_URL, FHIR_SERVER_USERNAME, FHIR_SERVER_PASSWORD);
        }
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Object translate(InputStream resourceInputStream) {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn(e.toString());
            return Response.status(500, e.toString()).build(); // Internal server error
        }

        try {
            Translation result = terminologyService.translate(resourceInputStream);
            logger.info("Resource translation successful");
            return result.getTranslatedResource().toPrettyString();
        } catch (Exception e) {
            logger.warn(e.toString());
            return Response.status(400, e.toString()).build(); // Bad request error
        }
    }

    @GET
    @Path("healthCheck")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHealthCheck() {
        try {
            initializeService();
        } catch (Exception e) {
            logger.warn(e.toString());
            return Response.status(500, e.toString()).build(); // Internal server error
        }

        StringWriter status = new StringWriter();
        if (terminologyService.healthCheck(status)) {
            logger.info("Terminology microservice is functional");
            return Response.status(200).build(); // OK
        } else {
            logger.warn(status.toString());
            return Response.status(500, status.toString()).build(); // Internal server error
        }
    }

}
