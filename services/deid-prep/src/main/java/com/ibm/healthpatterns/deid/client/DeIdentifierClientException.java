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
package com.ibm.healthpatterns.deid.client;

/**
 * Indicates that an error occurred in the {@link DeIdentifierServiceClient}.
 * 
 * @author Luis A. García
 */
public class DeIdentifierClientException extends Exception {

	/**
	 * 
	 */
	private static final long serialVersionUID = -3904998271976616044L;

	/**
	 * @param msg
	 */
	public DeIdentifierClientException(String msg) {
		super(msg);
	}

	/**
	 * @param msg 
	 * @param cause 
	 */
	public DeIdentifierClientException(String msg, Exception cause) {
		super(msg, cause);
	}
}
