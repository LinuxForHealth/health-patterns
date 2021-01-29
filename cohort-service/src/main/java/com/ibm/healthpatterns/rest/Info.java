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
package com.ibm.healthpatterns.rest;

import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.boot.context.event.ApplicationReadyEvent;

/**
 * 
 * @author Luis A. García
 */
@Component
public class Info {

	/**
	 * 
	 */
	@EventListener(ApplicationReadyEvent.class)
	public void contextRefreshedEvent() {
		System.out.println("The following endpoints are available by default :-");
		System.out.println("  Health        : http://localhost:8080/health");
		System.out.println("  Application   : http://localhost:8080/cohort-service/config");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries/{id}/patients");
		System.out.println("  Application   : http://localhost:8080/cohort-service/libraries/{id}/patientIds");
	}

}
