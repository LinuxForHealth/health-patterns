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

import categories.BasicEnrichment;
import categories.ASCVDEnrichment;
import categories.EnrichmentConfig;
import categories.EnrichmentInit;
import categories.NLPEnrichment;
import categories.NLPEnrichmentFVT;
import categories.FHIRTrigger;


@TargetEnv("enrich-flow.properties")
@RunWith(ZeroCodeUnitRunner.class)

public class Enrich_Flow {
	
	 @Test
	 @Category({EnrichmentInit.class})
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
	 @Category({EnrichmentInit.class})
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
	
	@Test
	 @Category({NLPEnrichment.class,NLPEnrichmentFVT.class})
	 @Scenario("scenarios/enrich_NLP_Insights_healthCheck.json")
	    public void enrich_NLP_Insights_healthCheck() throws Exception {
	    }
	
	@Test
	 @Category({NLPEnrichment.class,NLPEnrichmentFVT.class})
	 @Scenario("scenarios/enrich_NLP_Insights_Config_CRUD.json")
	    public void enrich_NLP_Insights_Config_CRUD() throws Exception {
	    }

	@Test
	 @Category({NLPEnrichment.class,NLPEnrichmentFVT.class})
	 @Scenario("scenarios/enrich_NLP_Insights_Config_Errors.json")
	    public void enrich_NLP_Insights_Config_Errors() throws Exception {
	    }

	@Test
	 @Category({NLPEnrichment.class})
	 @Scenario("scenarios/enrich_NLP_Insights_Config_Use.json")
	    public void enrich_NLP_Insights_Config_Use() throws Exception {
	    }

	
	@Test
	 @Category({NLPEnrichment.class,NLPEnrichmentFVT.class})
	 @Scenario("scenarios/enrich_NLP_Insights_Override_CRUD.json")
	    public void enrich_NLP_Insights_Override_CRUD() throws Exception {
	    }
	
	@Test
	 @Category({NLPEnrichment.class})
	 @Scenario("scenarios/enrich_NLP_Insights_Override_Use.json")
	    public void enrich_NLP_Insights_Override_Use() throws Exception {
	    }
	
	@Test
	 @Category({FHIRTrigger.class})
	 @Scenario("scenarios/enrich_FHIR_Trigger.json")
	    public void enrich_FHIR_Trigger() throws Exception {
	    }
}
