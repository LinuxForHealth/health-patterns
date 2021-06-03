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
package com.ibm.healthpatterns.microservices.terminology;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * The result of a translation operation.
 * <p>
 * A {@link Translation} operation consists of finding <code>valueCode</code> extensions
 * in a FHIR resource (bundle or an individual resource) that belong to a
 * ValueSet This object contains the elements that may be important to a
 * requester of a de-identify operation such as the initial resource, the
 * de-identified resource, and any FHIR responses.
 * 
 * @author Luis A. García
 */
public class Translation {

	private JsonNode originalResource;
	private JsonNode translatedResource;
	
	/**
	 * @param originalResource
	 * @param translatedResource
	 */
	public Translation(JsonNode originalResource, JsonNode translatedResource) {
		this.originalResource = originalResource;
		this.translatedResource = translatedResource;
	}

	/**
	 * @return the originalResource
	 */
	public JsonNode getOriginalResource() {
		return originalResource;
	}

	/**
	 * @return the translated resource, or null if not a single valueCode was found that could be translated
	 */
	public JsonNode getTranslatedResource() {
		return translatedResource;
	}
}
