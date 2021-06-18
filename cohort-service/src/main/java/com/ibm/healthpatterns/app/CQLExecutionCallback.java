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

import java.util.List;

import com.ibm.cohort.engine.EvaluationResultCallback;

/**
 * Defines the behavior that is executed for each CQL expression on each context (patient).
 * 
 * @author Luis A. García
 */
class CQLExecutionCallback implements EvaluationResultCallback {
	
	/**
	 * 
	 */
	private final List<String> cohort;
	private boolean reverseMatch;
	
	private Boolean numerator;
	private Boolean denominator;

	/**
	 * @param cohort a list where the matching patients will be saved in place 
	 * @param reverseMatch save the patients who don't match the cohort
	 */
	CQLExecutionCallback(List<String> cohort, boolean reverseMatch) {
		this.cohort = cohort;
		this.reverseMatch = reverseMatch;
	}

	@Override
	public void onContextBegin(String contextId) {
		numerator = null;
		denominator = null;
	}

	@Override
	public void onEvaluationComplete(String contextId, String expression, Object result) {
		
		if (expression.equalsIgnoreCase("Numerator") || expression.equalsIgnoreCase("InPopulation")) {
			numerator = Boolean.parseBoolean(result.toString());
		} else if (expression.equalsIgnoreCase("Denominator") || expression.equalsIgnoreCase("MeetsInclusionCriteria")) {
			denominator = Boolean.parseBoolean(result.toString());
		}
		
		if (numerator != null && denominator != null) {
			if (!denominator) {
				return;
			}
			if ((numerator && !reverseMatch) || (!numerator && reverseMatch)) {
				cohort.add(contextId);
				return;
			}
		}
	}

	@Override
	public void onContextComplete(String contextId) {
	}
}

