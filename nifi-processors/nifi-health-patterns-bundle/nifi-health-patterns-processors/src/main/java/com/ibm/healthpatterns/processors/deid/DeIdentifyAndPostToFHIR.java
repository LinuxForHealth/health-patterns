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
package com.ibm.healthpatterns.processors.deid;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

import org.apache.nifi.annotation.behavior.InputRequirement;
import org.apache.nifi.annotation.behavior.InputRequirement.Requirement;
import org.apache.nifi.annotation.behavior.WritesAttribute;
import org.apache.nifi.annotation.behavior.WritesAttributes;
import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.logging.ComponentLog;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.io.InputStreamCallback;
import org.apache.nifi.processor.io.OutputStreamCallback;
import org.apache.nifi.processor.util.StandardValidators;
import org.apache.nifi.util.FormatUtils;
import org.apache.nifi.util.StopWatch;

import com.fasterxml.jackson.databind.JsonNode;
import com.ibm.healthpatterns.deid.DeIdentification;
import com.ibm.healthpatterns.deid.DeIdentifier;
import com.ibm.healthpatterns.deid.DeIdentifierException;

/**
 * Custom processor to deidentify a FHIR resource and save it to a FHIR server.
 * 
 * @author Luis A. García
 */
@Tags({"fhir", "deid", "ibm", "alvearie"})
@CapabilityDescription("De-identifies the given FHIR resources and adds them to a designated FHIR server.")
@InputRequirement(Requirement.INPUT_REQUIRED)
@WritesAttributes({
    @WritesAttribute(attribute = "location", description = "The HTTP Location header returned by the FHIR server when a resource is created"),
    @WritesAttribute(attribute = "deidTransactwionId", description = "All FlowFiles produced from the deidentifying and persisting the same parent FlowFile will have the same randomly generated UUID added for this attribute")})
public class DeIdentifyAndPostToFHIR extends AbstractProcessor {

	private static final PropertyDescriptor FHIR_URL = new PropertyDescriptor.Builder()
			.name("Deidentified FHIR Server URL")
			.description("The URL of the FHIR server that will be used to persist the deidentified FHIR resources.")
			.required(true)
			.defaultValue("http://ingestion-fhir-deid/fhir-server/api-v4")
			.addValidator(StandardValidators.URI_VALIDATOR)
			.build();

	private static final PropertyDescriptor FHIR_USERNAME = new PropertyDescriptor.Builder()
			.name("Deidentified FHIR Server Username")
			.description("The username of the FHIR server that will be used to persist the deidentified FHIR resources.")
			.required(true)
			.defaultValue("fhiruser")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	private static final PropertyDescriptor FHIR_PASSWORD = new PropertyDescriptor.Builder()
			.name("Deidentified FHIR Server Password")
			.description("The password of the FHIR server that will be used to persist the deidentified FHIR resources.")
			.required(true)
			.sensitive(true)
			.defaultValue("integrati0n")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	private static final Relationship ORIGINAL = new Relationship.Builder()
			.name("original")
			.description("The original input file will be routed to this destination when it has been deidentified and"
					+ "persisted to the DEID FHIR server.")
			.build();

	private static final Relationship DEIDENTIFIED = new Relationship.Builder()
			.name("deidentified")
			.description("The deidentified FHIR resource prior to it being persisted in the DEID FHIR server.")
			.build();

	private static final Relationship SUCCESS = new Relationship.Builder()
			.name("success")
			.description("The response from the FHIR server and if applicable the Location header of the new FHIR resource "
					+ "will be sent here if the original FHIR resource was successfully deidentified and persisted to the "
					+ "DEID FHIR server.")
			.build();

	private static final Relationship FAILURE = new Relationship.Builder()
			.name("failure")
			.description("The original file will be routed here if there was a problem de-identifying the FHIR resource "
					+ "or persisting it to the DEID FHIR server.")
			.build();

	private List<PropertyDescriptor> descriptors;
	private Set<Relationship> relationships;

	private volatile DeIdentifier deid;
	/**
	 * Initialize the processor with the four properties and two relationships defined above
	 * @param context the processor context
	 */
	@Override
	protected void init(final ProcessorInitializationContext context) {
		List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
		descriptors.add(FHIR_URL);
		descriptors.add(FHIR_USERNAME);
		descriptors.add(FHIR_PASSWORD);
		this.descriptors = Collections.unmodifiableList(descriptors);

		Set<Relationship> relationships = new HashSet<Relationship>();
		relationships.add(SUCCESS);
		relationships.add(FAILURE);
		relationships.add(ORIGINAL);
		relationships.add(DEIDENTIFIED);
		this.relationships = Collections.unmodifiableSet(relationships);
	}

	/**
	 * This method returns the relationships that have been defined
	 * @return a set of relationships for this processor
	 */
	@Override
	public Set<Relationship> getRelationships() {
		return this.relationships;
	}

	/**
	 * This method returns the properties that have been defined
	 * @return a list of properties
	 */
	@Override
	public final List<PropertyDescriptor> getSupportedPropertyDescriptors() {
		return descriptors;
	}

	/**
	 * 
	 * @param context
	 */
	@OnScheduled
	public void onScheduled(final ProcessContext context) {
		deid = new DeIdentifier();
	}

	/*
	 * (non-Javadoc)
	 * @see org.apache.nifi.processor.AbstractProcessor#onTrigger(org.apache.nifi.processor.ProcessContext, org.apache.nifi.processor.ProcessSession)
	 */
	@Override
	public void onTrigger(final ProcessContext context, final ProcessSession session) {
		FlowFile flowFile = session.get();
		if (flowFile == null) {
			return;
		}

		final ComponentLog logger = getLogger();
		AtomicBoolean error = new AtomicBoolean();
		AtomicReference<DeIdentification> deidentificationRef = new AtomicReference<>();
		AtomicReference<String> uploadDataRate = new AtomicReference<String>();
		AtomicLong uploadMillis = new AtomicLong();
		
		final StopWatch stopWatch = new StopWatch(true);
		session.read(flowFile, new InputStreamCallback() {

			/*
			 * (non-Javadoc)
			 * @see org.apache.nifi.processor.io.InputStreamCallback#process(java.io.InputStream)
			 */
			@Override
			public void process(InputStream in) throws IOException {
				DeIdentification deidentification = null;
				try {
					deidentification = deid.deIdentify(in);
				} catch (DeIdentifierException e) {
					error.set(true);
					logger.error(e.getMessage() + " Routing to failure.", e)	;
				}
				stopWatch.stop();
				uploadMillis.set(stopWatch.getDuration(TimeUnit.MILLISECONDS));
				uploadDataRate.set(stopWatch.calculateDataRate(flowFile.getSize()));
				deidentificationRef.set(deidentification);			
			}
		});

		if (error.get()) {
			session.transfer(flowFile, FAILURE);
			return;
		}
		logger.info("Successfully de-identified and persisted to FHIR in {} at a rate of {}",
				new Object[]{flowFile, FormatUtils.formatMinutesSeconds(uploadMillis.get(), TimeUnit.MILLISECONDS), uploadDataRate.get()});

		String transactionId = UUID.randomUUID().toString();
		DeIdentification deidentification = deidentificationRef.get();

		session.putAttribute(flowFile, "deidTransactionID", transactionId);
		session.transfer(flowFile, ORIGINAL);
		
		JsonNode deidResource = deidentification.getDeIdentifiedResource();
		FlowFile deidFlowFile = session.create(flowFile);
		deidFlowFile = session.write(deidFlowFile, new OutputStreamCallback() {

			/*
			 * (non-Javadoc)
			 * @see org.apache.nifi.processor.io.OutputStreamCallback#process(java.io.OutputStream)
			 */
			@Override
			public void process(OutputStream out) throws IOException {
				try (OutputStream outputStream = new BufferedOutputStream(out)) {
					outputStream.write(deidResource.toPrettyString().getBytes(StandardCharsets.UTF_8));
				}				
			}
		});
		session.putAttribute(deidFlowFile, "deidTransactionID", transactionId);
		session.putAttribute(deidFlowFile, "mime.type", "application/json");
		session.transfer(deidFlowFile, DEIDENTIFIED);

		JsonNode fhirResponse = deidentification.getFhirResponse();
		String fhirLLocationHeader = deidentification.getFhirLocationHeader();
		FlowFile fhirResponseFlowFile = session.create(flowFile);
		fhirResponseFlowFile = session.write(fhirResponseFlowFile, new OutputStreamCallback() {

			/*
			 * (non-Javadoc)
			 * @see org.apache.nifi.processor.io.OutputStreamCallback#process(java.io.OutputStream)
			 */
			@Override
			public void process(OutputStream out) throws IOException {
				try (OutputStream outputStream = new BufferedOutputStream(out)) {
					outputStream.write(fhirResponse.toPrettyString().getBytes(StandardCharsets.UTF_8));
				}				
			}
		});
		session.putAttribute(fhirResponseFlowFile, "deidTransactionID", transactionId);
		session.putAttribute(fhirResponseFlowFile, "Location", fhirLLocationHeader);
		session.putAttribute(deidFlowFile, "mime.type", "application/json");
		session.transfer(fhirResponseFlowFile, SUCCESS);
	}
}
