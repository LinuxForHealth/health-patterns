package org.alvearie.healthpatterns;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;

import javax.validation.constraints.NotNull;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.cloud.objectstorage.ClientConfiguration;
import com.ibm.cloud.objectstorage.SDKGlobalConfiguration;
import com.ibm.cloud.objectstorage.SdkClientException;
import com.ibm.cloud.objectstorage.auth.AWSCredentials;
import com.ibm.cloud.objectstorage.auth.AWSStaticCredentialsProvider;
import com.ibm.cloud.objectstorage.client.builder.AwsClientBuilder;
import com.ibm.cloud.objectstorage.oauth.BasicIBMOAuthCredentials;
import com.ibm.cloud.objectstorage.services.s3.AmazonS3;
import com.ibm.cloud.objectstorage.services.s3.AmazonS3ClientBuilder;
import com.ibm.cloud.objectstorage.services.s3.model.GetObjectRequest;
import com.ibm.cloud.objectstorage.services.s3.model.S3Object;

/**
 * @author atclark
 *
 * This class contains a REST API to retrieve all ICD10 codes for a supplied Snomed code. It directly relies on a mapping file downloaded from UMLS and stored in cloud object storage (COS).
 * 
 * To build, run: ./mvnw package
 * To run in dev mode, run: ./mvnw compile quarkus:dev  
 */
@Path("/direct")
public class SnomedToICD10Direct {

    public static final String CODE = "code";
    private static final Logger LOG = Logger.getLogger(SnomedToICD10Direct.class.getName());
    private static final String BUCKET_NAME = "fhir-term-graph";
    private static final String SNOMED_TO_ICD_MAP_FILE = "der2_iisssccRefset_ExtendedMapFull_US1000124_20210901.txt";
    private static final String UMLS_DELIMITER = "\t";

    private static String COS_ENDPOINT = "https://s3.us-east.cloud-object-storage.appdomain.cloud"; // eg
												    // "https://s3.us.cloud-object-storage.appdomain.cloud"
    private static String COS_API_KEY_ID = "KrgAwCqAIxyRI866y0oVaeQopHokkqFNiReyQuwHQnDY"; // eg
											   // "0viPHOY7LbLNa9eLftrtHPpTjoGv6hbLD1QalRXikliJ"
    private static String COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token";
    private static String COS_SERVICE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/6694a1bda7d84197b130c3ea87ef3e77:131a8d10-c8ff-4e05-b344-921abdd60bcc::"; // "crn:v1:bluemix:public:cloud-object-storage:global:a/<CREDENTIAL_ID_AS_GENERATED>:<SERVICE_ID_AS_GENERATED>::"
    private static String COS_BUCKET_LOCATION = "us"; // eg "us"

    private static Map<String, Set<String>> SNOMED_TO_ICD = null;
    private static final ObjectMapper mapper = new ObjectMapper();

    // Create client connection
    public static AmazonS3 createClient(String api_key, String service_instance_id, String endpoint_url,
	    String location) {
	AWSCredentials credentials;
	credentials = new BasicIBMOAuthCredentials(api_key, service_instance_id);

	ClientConfiguration clientConfig = new ClientConfiguration().withRequestTimeout(5000);
	clientConfig.setUseTcpKeepAlive(true);

	AmazonS3 cosClient = AmazonS3ClientBuilder.standard()
		.withCredentials(new AWSStaticCredentialsProvider(credentials))
		.withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint_url, location))
		.withPathStyleAccessEnabled(true).withClientConfiguration(clientConfig).build();
	return cosClient;
    }

    public static InputStreamReader getItem(String bucketName, String itemName) {
	System.out.printf("Retrieving item from bucket: %s, key: %s\n", bucketName, itemName);

	SDKGlobalConfiguration.IAM_ENDPOINT = COS_AUTH_ENDPOINT;

	try {
	    AmazonS3 _cos = createClient(COS_API_KEY_ID, COS_SERVICE_CRN, COS_ENDPOINT, COS_BUCKET_LOCATION);
	    S3Object item = _cos.getObject(new GetObjectRequest(bucketName, itemName));
	    return new InputStreamReader(item.getObjectContent());
	} catch (SdkClientException sdke) {
	    sdke.printStackTrace();
	}
	return null;
    }

    /**
     * This method loads the underlying Snomed->ICD10 map information from file.
     * 
     * 
     * 
     * @return
     */
    private static final Map<String, Set<String>> getMap() {
	if (SNOMED_TO_ICD != null) {
	    return SNOMED_TO_ICD;
	}
	synchronized (SnomedToICD10Direct.class) {

	    if (SNOMED_TO_ICD != null) {
		return SNOMED_TO_ICD;
	    }
	    // For a given snomed code, find the most recent active row. If the rule is
	    // always map to a single ICD code, add an edge. If not, skip that snomed code.

	    Map<String, String> snomedToDateMap = new HashMap<>(); // Snomed->ICD, date
	    Map<String, Set<String>> snomedToICDMap = new HashMap<>(); // Snomed->ICD, date

	    final AtomicInteger rowCount = new AtomicInteger(0);

	    InputStreamReader in = getItem(BUCKET_NAME, SNOMED_TO_ICD_MAP_FILE);

	    try (BufferedReader reader = new BufferedReader(in)) {
		reader.lines().forEach(line -> {
		    if (rowCount.incrementAndGet() % 10000 == 0) {
			LOG.info("Row Count: " + rowCount.get());
		    }

		    String[] tokens = line.split(UMLS_DELIMITER);
		    String active = tokens[2];
		    if (!active.equals("1")) { // Skip inactive rows
			return;
		    }
		    String effectiveTime = tokens[1];
		    String snomed = tokens[5];

		    String curEffectiveTime = null;
		    if (snomedToDateMap.containsKey(snomed)) {
			curEffectiveTime = snomedToDateMap.get(snomed);
		    }
		    if (curEffectiveTime != null && curEffectiveTime.compareTo(effectiveTime) > 0) {
		        // Only look at the most recent effectiveTime values for a given Snomed code
		        return;
		    }
		    if (curEffectiveTime != null && !effectiveTime.equals(curEffectiveTime)) {
			snomedToICDMap.remove(snomed);
		    }
		    snomedToDateMap.put(snomed, effectiveTime);

		    String mapRule = tokens[8];
		    if (!Boolean.parseBoolean(mapRule)) {
			return;
		    }
		    String advice = tokens[9];
		    String icd = tokens[10];
		    if (!advice.equals("ALWAYS " + icd)) {
		        // Only support map rows where the rules are ALWAYS mapping 
			return;
		    }
		    Set<String> icds = snomedToICDMap.computeIfAbsent(snomed, s -> new HashSet<>());
		    icds.add(icd);
		});
	    } catch (IOException e) {
		e.printStackTrace();
	    }
	    snomedToDateMap.clear(); // Don't need it any more, let GC clean it up
	    SNOMED_TO_ICD = snomedToICDMap;
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
    public static final String calculate(@NotNull @QueryParam(CODE) String snomedCode) throws JsonProcessingException {
	Set<String> icds = new HashSet<>();
	if (getMap().containsKey(snomedCode)) {
	    icds.addAll(getMap().get(snomedCode));
	}
	return mapper.writeValueAsString(icds);
    }
}