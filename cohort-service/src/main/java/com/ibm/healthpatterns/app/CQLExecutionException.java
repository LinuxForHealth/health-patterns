/**
 * 
 */
package com.ibm.healthpatterns.app;

/**
 * A problem that occurred executing a CQL file.
 * 
 * @author Luis A. Garía
 *
 */
public class CQLExecutionException extends Exception {

	/**
	 * 
	 */
	private static final long serialVersionUID = 3340318325099136254L;

	/**
	 * Create a {@link CQLExecutionException} from the given generic {@link Exception} thrown by the Cohort Engine.
	 * 
	 * @param e the underlying exception
	 */
	public CQLExecutionException(Exception e) {
		super(e.getMessage(), e.getCause());
	}
}
