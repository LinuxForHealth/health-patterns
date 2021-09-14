
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

import categories.BasicIngestionInit;

@TargetEnv("clinical-ingestion-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class Ingestion_Initialize {

	 @Test
	 @Category({BasicIngestionInit.class})
	 @Scenario("scenarios/ingest_HealthCheck.json")
	 
	    public void ingest_HealthCheck() throws Exception {
	    }
	 
}
