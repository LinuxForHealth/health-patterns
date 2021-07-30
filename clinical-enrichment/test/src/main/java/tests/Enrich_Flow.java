
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

import categories.BasicEnrichment;
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
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_ASCVD_New.json")
	    public void enrich_ASCVD_New() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicEnrichment.class})
	 @Scenario("scenarios/enrich_ASCVD_Update.json")
	    public void enrich_ASCVD_Update() throws Exception {
	    }
	 
	 @Test
	 @Category({EnrichmentConfig.class})
	 @Scenario("scenarios/enrich_DEID_Prep_Config_CRUD.json")
	    public void enrich_DEID_Config_CRUD() throws Exception {
	    }

}
