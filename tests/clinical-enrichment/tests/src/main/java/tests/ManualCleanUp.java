
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

//	 @Ignore
	 @Test
	 @Scenario("scenarios/deid_FHIR_Patient_DELETE.json")
	    public void deidPatientDELETE() throws Exception {
	 }
	 
//	 @Ignore
	 @Test
	 @Scenario("scenarios/pri_FHIR_Patient_DELETE.json")
	    public void priPatientDELETE() throws Exception {
	 }
	 
}
