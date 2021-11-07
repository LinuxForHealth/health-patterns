
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
import org.junit.Ignore;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import categories.BasicIngestion;
import categories.DeIDIngestion;
import categories.FHIRProxyIngestion;

@TargetEnv("clinical-ingestion-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class ManualCleanUp {
	 @Test
	 @Scenario("scenarios/oneLineTest.json")
	    public void one_liner_test() throws Exception {
	    }
	 
	 @Test
	 @Scenario("scenarios/ingest_FHIR_Patient_DELETE.json")
	    public void patientDELETE() throws Exception {
	 }	 
	 
	 @Test
	 @Scenario("scenarios/create_Kafka_Topic.json")
	    public void createKafkaTopic() throws Exception {
	 } 
	 
}
