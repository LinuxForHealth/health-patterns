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
	private boolean reverseMatch;

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
	}

	@Override
	public void onEvaluationComplete(String contextId, String expression, Object result) {
		if (expression.equalsIgnoreCase("Numerator")) {
			boolean patientMatched = Boolean.parseBoolean(result.toString());
			if ((patientMatched && !reverseMatch) || (!patientMatched && reverseMatch)) {
				cohort.add(contextId);
			}
		}
	}

	@Override
	public void onContextComplete(String contextId) {
	}
}

