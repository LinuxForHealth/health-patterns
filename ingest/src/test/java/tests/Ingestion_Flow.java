
/*
 * (C) Copyright IBM Corp. 2021,2022
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package tests;

import org.jsmart.zerocode.core.domain.Scenario;
import org.jsmart.zerocode.core.domain.TargetEnv;
import org.jsmart.zerocode.core.runner.ZeroCodeUnitRunner;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import categories.BasicIngestion;
import categories.BasicIngestionBLK;
import categories.DeIDIngestion;
import categories.DeIDIngestionBLK;
import categories.FHIRDataQualityBLK;
import categories.ASCVDIngestion;
import categories.ASCVDIngestionBLK;
import categories.NLPIngestion;
import categories.NLPIngestionBLK;
import categories.FHIRProxyIngestion;
import categories.FHIRCQL;

@TargetEnv("clinical-ingestion-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class Ingestion_Flow {
	
// Test categories that end with 'BLK' use the expose-kafka blocking-api 	
	
	
	 // Basic ingestion tests
	
	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_Errors.json")
	    public void ingest_FHIR_Errors() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_Errors_BLK.json")
	    public void ingest_FHIR_Errors_BLK() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR.json")
	    public void ingest_FHIR() throws Exception {
	    }
	 
	 @Test
	 @Category({BasicIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_BLK.json")
	    public void ingest_FHIR_BLK() throws Exception {
	    }

	 @Test
	 @Category({BasicIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_TERM.json")
	    public void ingest_FHIR_TERM() throws Exception {
	    }

	 @Test
	 @Category({BasicIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_TERM_BLK.json")
	    public void ingest_FHIR_TERM_BLK() throws Exception {
	    }
	 
	 
	 // DEID and Terminology ingestion tests
		
	 @Test
	 @Category({DeIDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_DEID.json")
	    public void ingest_FHIR_DEID() throws Exception {
	    }
	 
	 @Test
	 @Category({DeIDIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_DEID_BLK.json")
	    public void ingest_FHIR_DEID_BLK() throws Exception {
	    }
	
	 @Test
	 @Category({DeIDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_DEID_TERM.json")
	    public void ingest_FHIR_DEID_TERM() throws Exception {
	    }
	 
	 @Test
	 @Category({DeIDIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_DEID_TERM_BLK.json")
	    public void ingest_FHIR_DEID_TERM_BLK() throws Exception {
	    }
	 
	 
	 // ASCVD ingestion tests
		
	 @Test
	 @Category({ASCVDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_ASCVD.json")
	    public void ingest_FHIR_ASCVD() throws Exception {
	    }
	 
	 @Test
	 @Category({ASCVDIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_ASCVD_BLK.json")
	    public void ingest_FHIR_ASCVD_BLK() throws Exception {
	    }
	 
	 @Test
	 @Category({ASCVDIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_No_ASCVD.json")
	    public void ingest_FHIR_No_ASCVD() throws Exception {
	    }
	 
	 @Test
	 @Category({ASCVDIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_No_ASCVD_BLK.json")
	    public void ingest_FHIR_No_ASCVD_BLK() throws Exception {
	    }
	 
	 
	 // NLP Insights ingestion tests
		
	 @Test
	 @Category({NLPIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights.json")
	    public void ingest_FHIR_NLP_Insights() throws Exception {
	    }
	 	 
	 @Test
	 @Category({NLPIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights_BLK.json")
	    public void ingest_FHIR_NLP_Insights_BLK() throws Exception {
	    }
	 
	 @Test
	 @Category({NLPIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights_Override.json")
	    public void ingest_FHIR_NLP_Insights_Override() throws Exception {
	    }
	 
	 @Test
	 @Category({NLPIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights_Override_BLK.json")
	    public void ingest_FHIR_NLP_Insights_Override_BLK() throws Exception {
	    }
	
	 @Test
	 @Category({NLPIngestionBLK.class})
	 @Scenario("scenarios/ingest_FHIR_NLP_Insights_BLK_AdverseEvent.json")
	    public void ingest_FHIR_NLP_Insights_BLK_AdverseEvent() throws Exception {
	    }
	 
	 
	 // FHIR Proxy health tests
		
	 @Test
	 @Category({FHIRProxyIngestion.class})
	 @Scenario("scenarios/ingest_FHIR_Proxy.json")
	    public void ingest_FHIR_Proxy() throws Exception {
	    }
	 
	 //  FHIR Data Quality Tests
	 @Test
	 @Category({FHIRDataQualityBLK.class})
	 @Scenario("scenarios/ingest_FHIR_Data_Quality_BLK.json")
	    public void ingest_FHIR_Data_Quality_BLK() throws Exception {
	    }
	 
	 //  FHIR CQL Endpoint Tests
	 @Test
	 @Category({FHIRCQL.class})
	 @Scenario("scenarios/ingest_FHIR_BLK_CQL_$CQL.json")
	    public void ingest_FHIR_BLK_CQL_$CQL() throws Exception {
	    }
	 
	 @Test
	 @Category({FHIRCQL.class})
	 @Scenario("scenarios/ingest_FHIR_BLK_CQL_$EVAL.json")
	    public void ingest_FHIR_BLK_CQL_$EVAL() throws Exception {
	    }
	 
	 @Test
	 @Category({FHIRCQL.class})
	 @Scenario("scenarios/ingest_CQL_Bulk_Export.json")
	    public void ingest_CQL_Bulk_Export() throws Exception {
	 }
	 
}
