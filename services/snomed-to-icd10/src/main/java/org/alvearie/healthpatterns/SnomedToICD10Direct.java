package org.alvearie.healthpatterns;

import java.io.IOException;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import javax.validation.constraints.NotNull;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.fhir.term.graph.loader.impl.SnomedICD10MapTermGraphLoader;

/**
 * @author atclark
 *
 *         This class contains a REST API to retrieve all ICD10 codes for a
 *         supplied Snomed code. It directly relies on a mapping file downloaded
 *         from UMLS and stored in cloud object storage (COS).
 * 
 *         To build, run: ./mvnw package To run in dev mode, run: ./mvnw compile
 *         quarkus:dev
 */
@Path("/direct")
public class SnomedToICD10Direct {

    public static final String CODE = "code";
    private static final String BUCKET_NAME = "fhir-term-graph";

    private static Map<String, Set<String>> SNOMED_TO_ICD = null;
    private static final ObjectMapper mapper = new ObjectMapper();

    /**
     * This method loads the underlying Snomed->ICD10 map information from file.
     * 
     * @return
     */
    private static final Map<String, Set<String>> getMap() throws IOException {
        if (SNOMED_TO_ICD != null) {
            return SNOMED_TO_ICD;
        }
        synchronized (SnomedToICD10Direct.class) {
            if (SNOMED_TO_ICD != null) {
                return SNOMED_TO_ICD;
            }
            SNOMED_TO_ICD = SnomedICD10MapTermGraphLoader.loadMap(BUCKET_NAME);
        }
        return SNOMED_TO_ICD;
    }

    /**
     * Calculate the ICD10 code(s) for a given Snomed code
     *
     * @param snomedCode
     * @return ICD10 code(s)
     * @throws JsonProcessingException
     */
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public static final String calculate(@NotNull @QueryParam(CODE) String snomedCode) throws IOException, JsonProcessingException {
        Set<String> icds = new HashSet<>();
        if (getMap().containsKey(snomedCode)) {
            icds.addAll(getMap().get(snomedCode));
        }
        return mapper.writeValueAsString(icds);
    }
}