/*
 * (C) Copyright IBM Corp. 2021
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
package com.ibm.healthpatterns.app;

import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.junit.Test;

/**
 * @author Rick St3even
 */
public class CohortServiceAppTest {

	/**
	 * 
	 * @throws IOException
	 */
	//@Test
	public void testAllPatientsForFemaleCohort() throws IOException {
		CQLFile file = new CQLFile(Paths.get("src/test/resources/FemalePatients-1.0.0.cql"));
		assertEquals("FemalePatients", file.getName());
		assertEquals("1.0.0", file.getVersion());
		
		CohortService serv = CohortService.getInstance();
		CQLFile currLib = serv.getLibrary(file.getId());
		if (currLib == null) {
			serv.addLibrary(file.getContent());
		}
		List<String> emptyPatientList = new ArrayList<String>();
		try {
			String response = serv.getPatientsForCohort(file.getId(), emptyPatientList, false);
			System.out.println(response);
		} catch (CQLExecutionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			fail("Unexpected error");
		}
	}

}
