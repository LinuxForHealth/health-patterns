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
package com.ibm.healthpatterns.processors.terminology;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
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
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.components.ValidationContext;
import org.apache.nifi.components.ValidationResult;
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

import com.ibm.healthpatterns.core.FHIRService;
import com.ibm.healthpatterns.processors.common.FHIRServiceCustomProcessor;
import com.ibm.healthpatterns.terminology.TerminologyService;
import com.ibm.healthpatterns.terminology.TerminologyServiceException;
import com.ibm.healthpatterns.terminology.Translation;

/**
 * Custom processor to run the FHIR Terminology Service's $translate operation on a FHIR resource.
 * 
 * @author Luis A. García
 */
@Tags({"fhir", "terminology service", "conceptmap", "ibm", "alvearie"})
@CapabilityDescription("Runs a FHIR ConceptMap $translate operation on the given FHIR resources.")
@InputRequirement(Requirement.INPUT_REQUIRED)
@WritesAttributes({
	@WritesAttribute(attribute = FHIRTranslation.TRANSLATED_ATTRIBUTE, description = "A boolean property that will get set to true when a translation occurred.")})
public class FHIRTranslation extends AbstractProcessor implements FHIRServiceCustomProcessor {

	/**
	 * A boolean attribute that gets set with translation status.
	 */
	static final String TRANSLATED_ATTRIBUTE = "fhirTranslation";

	static final PropertyDescriptor FHIR_URL = new PropertyDescriptor.Builder()
			.name("FHIR Server URL")
			.description("The full base URL of the FHIR server that has the FHIR Terminology Service and ConceptMaps.")
			.required(true)
			.defaultValue("http://ingestion-fhir/fhir-server/api/v4")
			.addValidator(StandardValidators.URI_VALIDATOR)
			.build();

	static final PropertyDescriptor FHIR_USERNAME = new PropertyDescriptor.Builder()
			.name("FHIR Server Username")
			.description("The username of the FHIR server that has the FHIR Terminology Service and ConceptMaps.")
			.required(false)
			.defaultValue("fhiruser")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	static final PropertyDescriptor FHIR_PASSWORD = new PropertyDescriptor.Builder()
			.name("FHIR Server Password")
			.description("The password of the FHIR server that has the FHIR Terminology Service and ConceptMaps.")
			.required(false)
			.sensitive(true)
			.defaultValue("integrati0n")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	static final Relationship SUCCESS = new Relationship.Builder()
			.name("success")
			.description("The given FHIR resource with its corresponding 'codeValue's values modified per running the "
					+ "FHIR Terminology Service's $translsate over a matching ConceptMap resource. See the following"
					+ "for reference: http://hl7.org/fhir/terminology-service.html#translate")
			.build();

	static final Relationship FAILURE = new Relationship.Builder()
			.name("failure")
			.description("The original file will be routed here if there was a problem running the FHIR Terminology "
					+ "Service $translate operation.")
			.build();

	private List<PropertyDescriptor> descriptors;
	private Set<Relationship> relationships;

	private volatile TerminologyService terminologyService;
	
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

	@Override
	protected Collection<ValidationResult> customValidate(final ValidationContext context) {
		final List<ValidationResult> results = new ArrayList<>(super.customValidate(context));

		String fhirURL = context.getProperty(FHIR_URL).getValue();
		String fhirUsername = context.getProperty(FHIR_USERNAME).getValue();
		String fhirPassword = context.getProperty(FHIR_PASSWORD).getValue();
		terminologyService = new TerminologyService(fhirURL, fhirUsername, fhirPassword);

		StringWriter status = new StringWriter();
		boolean healthOK = terminologyService.healthCheck(status);

		if (!healthOK) {
			ValidationResult validation = new ValidationResult.Builder()
					.subject("The connection information")
					.valid(false)
					.explanation("the health checks did not pass:\n" + status)
					.build();
			results.add(validation);			
		}

		return results;
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

		ComponentLog logger = getLogger();
		AtomicBoolean error = new AtomicBoolean();
		AtomicReference<Translation> translation = new AtomicReference<Translation>();
		AtomicReference<String> uploadDataRate = new AtomicReference<String>();
		AtomicLong uploadMillis = new AtomicLong();
		
		StopWatch stopWatch = new StopWatch(true);
		session.read(flowFile, new InputStreamCallback() {

			@Override
			public void process(InputStream in) throws IOException {
				Translation t9n = null;
				try {
					t9n = terminologyService.translate(in);
				} catch (TerminologyServiceException e) {
					error.set(true);
					logger.error("Error FHIR translating flow file {} will route to failure: {}", new Object[]{flowFile, e.getMessage()}, e);
				}
				stopWatch.stop();
				uploadMillis.set(stopWatch.getDuration(TimeUnit.MILLISECONDS));
				uploadDataRate.set(stopWatch.calculateDataRate(flowFile.getSize()));
				translation.set(t9n);
			}
		});

		if (error.get()) {
			session.transfer(flowFile, FAILURE);
			return;
		}
		logger.info("Successfully run FHIR Terminology Service $translation over flow file {} in {} at a rate of {}",
				new Object[]{flowFile, FormatUtils.formatMinutesSeconds(uploadMillis.get(), TimeUnit.MILLISECONDS), uploadDataRate.get()});

		boolean translated = translation.get().getTranslatedResource() != null;
		if (translated) {
			// We will only overwrite the original flow file iff there were some actual translations performed by the service
			session.write(flowFile, new OutputStreamCallback() {
				
				@Override
				public void process(OutputStream out) throws IOException {
					try (OutputStream outputStream = new BufferedOutputStream(out)) {
						outputStream.write(translation.get().getTranslatedResource().toPrettyString().getBytes(StandardCharsets.UTF_8));
					}				
				}
			});
			session.getProvenanceReporter().modifyContent(flowFile, uploadMillis.get());
		}
		session.putAttribute(flowFile, TRANSLATED_ATTRIBUTE, Boolean.toString(translated));
        session.transfer(flowFile, SUCCESS);		
	}

	/**
	 * @return the TS used by this custom processor
	 */
	TerminologyService getTerminologyService() {
		return terminologyService;
	}

	/* (non-Javadoc)
	 * @see com.ibm.healthpatterns.processors.common.FHIRServiceCustomProcessor#getFHIRService()
	 */
	@Override
	public FHIRService getFHIRService() {
		return getTerminologyService();
	}
}
