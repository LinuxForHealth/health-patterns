
/*******************************************************************************
 * IBM Confidential OCO Source Materials
 * 5737-D31, 5737-A56
 * (C) Copyright IBM Corp. 2020
 *
 * The source code for this program is not published or otherwise
 * divested of its trade secrets, irrespective of what has
 * been deposited with the U.S. Copyright Office.
 *******************************************************************************/
package tests;

import org.jsmart.zerocode.core.domain.Scenario;
import org.jsmart.zerocode.core.domain.TargetEnv;
import org.jsmart.zerocode.core.runner.ZeroCodeUnitRunner;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import categories.BasicIngestion;
import categories.DeIDIngestion;
import categories.ASCVDIngestion;
import categories.NLPIngestion;
import categories.FHIRProxyIngestion;

@TargetEnv("clinical-ingestion-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class Ingestion_Flow {
	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_Errors.json")
	    public void ingest_FHIR_Errors() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR.json")
	    public void ingest_FHIR() throws Exception {
	    }

	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_TERM.json")
	    public void ingest_FHIR_TERM() throws Exception {
	    }
	 
	 @Test
	 @Category({DeIDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_DEID.json")
	    public void ingest_FHIR_DEID() throws Exception {
	    }
	
	 @Test
	 @Category({DeIDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_DEID_TERM.json")
	    public void ingest_FHIR_DEID_TERM() throws Exception {
	    }
	 

	 @Test
	 @Category({ASCVDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_ASCVD.json")
	    public void ingest_FHIR_ASCVD() throws Exception {
	    }
	 
	 @Test
	 @Category({ASCVDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_No_ASCVD.json")
	    public void ingest_FHIR_No_ASCVD() throws Exception {
	    }
	 
	 @Test
	 @Category({FHIRProxyIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_Proxy.json")
	    public void ingest_FHIR_Proxy() throws Exception {
	    }
	 
	 @Test
	 @Category({NLPIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights.json")
	    public void ingest_FHIR_NLP_Insights() throws Exception {
	    }
	 
	 @Test
	 @Category({NLPIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights_Override.json")
	    public void ingest_FHIR_NLP_Insights_Override() throws Exception {
	    }
}
