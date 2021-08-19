
/*******************************************************************************
 * jUnit Java Driver for the Zerocode-based Enrichemnt tests
 *******************************************************************************/
package tests;

import org.jsmart.zerocode.core.domain.Scenario;
import org.jsmart.zerocode.core.domain.TargetEnv;
import org.jsmart.zerocode.core.runner.ZeroCodeUnitRunner;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import categories.BasicEnrichment;
import categories.ASCVDEnrichment;
import categories.EnrichmentConfig;


@TargetEnv("enrich-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class Enrich_Flow {
	
	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_DEID_Prep_healthCheck.json")
	    public void enrich_DEID_Prep_Health() throws Exception {
	    }

	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_DEID_Prep_Store_Patient.json")
	    public void enrich_DEID_Prep_Store_Patient() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_DEID_Prep_No_Store_Patient.json")
	    public void enrich_DEID_Prep_No_Store_Patient() throws Exception {
	    }

	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_TERM_Prep_healthCheck.json")
	    public void enrich_TERM_Prep_healthCheck() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_TERM_Prep.json")
	    public void enrich_TERM_Prep() throws Exception {
	    }
	  
	 @Test
	 @Category({ASCVDEnrichment.class})
	 @Scenario("scenarios/enrich_ASCVD_New.json")
	    public void enrich_ASCVD_New() throws Exception {
	    }
	 
	 @Test
	 @Category({ASCVDEnrichment.class})
	 @Scenario("scenarios/enrich_ASCVD_Update.json")
	    public void enrich_ASCVD_Update() throws Exception {
	    }
	    
	 
	 @Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_DEID_Prep_Config_CRUD.json")
	    public void enrich_DEID_Config_CRUD() throws Exception {
	    }
	 
	 
	 @Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_DEID_Prep_Config_Use.json")
	    public void enrich_DEID_Config_Use() throws Exception {
	    }
	    
	@Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_TERM_Prep_Map_CRUD.json")
	    public void enrich_TERM_Prep_Map_CRUD() throws Exception {
	    }
	
	@Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_TERM_Prep_SD_CRUD.json")
	    public void enrich_TERM_Prep_SD_CRUD() throws Exception {
	    }
	
	@Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_TERM_Prep_SD_Use.json")
	    public void enrich_TERM_Prep_SD_Use() throws Exception {
	    }

}
