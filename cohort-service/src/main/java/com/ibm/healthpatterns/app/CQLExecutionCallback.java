package com.ibm.healthpatterns.app;

import java.util.List;

import com.ibm.cohort.engine.EvaluationResultCallback;

/**
 * Defines the behavior that is executed for each CQL expression on each context (patient).
 * 
 * @author Luis A. Garía
 *
 */
class CQLExecutionCallback implements EvaluationResultCallback {
	
	/**
	 * 
	 */
	private final List<String> cohort;

	/**
	 * @param cohort
	 */
	CQLExecutionCallback(List<String> cohort) {
		this.cohort = cohort;
	}

	@Override
	public void onContextBegin(String contextId) {
	}

	@Override
	public void onEvaluationComplete(String contextId, String expression, Object result) {
		if (expression.equalsIgnoreCase("Numerator") && Boolean.parseBoolean(result.toString())) {
			cohort.add(contextId);
		}
	}

	@Override
	public void onContextComplete(String contextId) {
	}
}

