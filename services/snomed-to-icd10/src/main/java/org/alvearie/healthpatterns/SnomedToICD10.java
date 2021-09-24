package org.alvearie.healthpatterns;

import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.validation.constraints.NotNull;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import org.apache.commons.configuration2.Configuration;
import org.apache.commons.configuration2.ex.ConfigurationException;
import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;
import org.apache.tinkerpop.gremlin.structure.Direction;
import org.apache.tinkerpop.gremlin.structure.Edge;
import org.apache.tinkerpop.gremlin.structure.Vertex;

import com.ibm.fhir.term.graph.FHIRTermGraph;
import com.ibm.fhir.term.graph.factory.FHIRTermGraphFactory;
import com.ibm.fhir.term.graph.loader.impl.SnomedICD10MapTermGraphLoader;
import com.ibm.fhir.term.graph.loader.util.ConfigLoader;

/**
 * @author atclark
 *
 * This class contains a REST API to connect to a configured Term Graph and retrieve all ICD10 codes for a supplied Snomed code
 * 
 * To build, run: ./mvnw package
 * To run in dev mode, run: ./mvnw compile quarkus:dev  
 */
@Path("/")
public class SnomedToICD10 {

    public static final String CODE = "code";
    private static final Logger LOG = Logger.getLogger(SnomedToICD10.class.getName());

    private FHIRTermGraph graph = null;
    private GraphTraversalSource g = null;

    public SnomedToICD10() throws ConfigurationException {
        Configuration configuration = ConfigLoader.load("conf/janusgraph-cassandra-elasticsearch.properties");
        graph = FHIRTermGraphFactory.open(configuration);
        g = graph.traversal();
    }

    
    /**
     * Calculate the ICD10 code(s) for a given Snomed code
     *
     * @param snomedCode
     * @return ICD10 code(s) 
     */
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public final String calculate(@NotNull @QueryParam(CODE) String snomedCode) {
        try {
            List<Vertex> snoMedConcepts = g.V().has(CODE, snomedCode).toList();
            Vertex snoMedConcept = snoMedConcepts.get(0);

            Iterator<Edge> edges = snoMedConcept.edges(Direction.IN, SnomedICD10MapTermGraphLoader.MAPS_TO);
            while (edges.hasNext()) {
                Edge edge = edges.next();
                Vertex outConcept = edge.outVertex();
                Object value = outConcept.value(CODE);
                return value.toString();
            }
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "Error finding edge", e);
        }
        return "";
    }
}