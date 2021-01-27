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

/**
 * A problem that occurred executing a CQL file.
 * 
 * @author Luis A. García
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
