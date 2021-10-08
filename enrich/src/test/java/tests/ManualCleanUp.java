
/*******************************************************************************
 * jUnit Driver for Tests that perform enrichment environment cleanup (executed manually)
 *******************************************************************************/
package tests;

import org.jsmart.zerocode.core.domain.Scenario;
import org.jsmart.zerocode.core.domain.TargetEnv;
import org.jsmart.zerocode.core.runner.ZeroCodeUnitRunner;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

@TargetEnv("enrich-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class ManualCleanUp {


	 @Test
	 @Scenario("scenarios/deid_FHIR_Patient_DELETE.json")
	    public void deidPatientDELETE() throws Exception {
	 }
	 
	 @Test
	 @Scenario("scenarios/pri_FHIR_Patient_DELETE.json")
	    public void priPatientDELETE() throws Exception {
	 }
	
	 @Test
	 @Scenario("scenarios/enrich_TERM_Prep_Map_Change.json")
	    public void enrich_TERM_Prep_Map_Change() throws Exception {
	 }
		
	 @Test
	 @Scenario("scenarios/enrich_TERM_Prep_Map_Restore.json")
	    public void enrich_TERM_Prep_Map_Restore() throws Exception {
	 }
		
	 @Test
	 @Scenario("scenarios/enrich_TERM_Prep_Map_Enrich.json")
	    public void enrich_TERM_Prep_Map_Enrich() throws Exception {
	 }
	 
	 @Test
	 @Scenario("scenarios/enrich_NLP_Insights.json")
	 	public void enrich_NLP_Insights() throws Exception {
	 }
}
