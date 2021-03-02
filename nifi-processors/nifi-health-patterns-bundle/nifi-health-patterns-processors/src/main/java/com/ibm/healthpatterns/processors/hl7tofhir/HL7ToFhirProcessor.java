/*
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
package com.ibm.healthpatterns.processors.hl7tofhir;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.flowfile.attributes.CoreAttributes;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.io.InputStreamCallback;
import org.apache.nifi.processor.io.OutputStreamCallback;
import org.apache.nifi.util.FormatUtils;
import org.apache.nifi.util.StopWatch;
import ca.uhn.hl7v2.HL7Exception;
import io.github.linuxforhealth.hl7.HL7ToFHIRConverter;
import io.github.linuxforhealth.hl7.parsing.HL7HapiParser;

/**
 * This custom nifi processor will convert HL7 messages to FHIR messages using the Open Source HL7 to FHIR converter (https://github.com/LinuxForHealth/hl7v2-fhir-converter). The flow file passed in
 * should contain HL7 data. The response will be: 
 * 
 * "success" - If the flowfile is successfully converted to FHIR, the flowfile will contain the FHIR version of the input data. 
 * "HL7 data not detected" - If the flowfile cannot be parsed as HL7 data, the input flowfile will be returned with this response.
 * "failure" - If the conversion fails for any reason, the input flowfile will be returned with this response. Errors will be written to the log.
 */

@Tags({ "HL7ToFhirprocessor" })
public class HL7ToFhirProcessor extends AbstractProcessor {
    public static String VERSION = "HL7ToFhirProcessor V0.0.1";

    public static final Relationship SUCCESS_RELATIONSHIP = new Relationship.Builder().name("success").description("HL7 data converted successfully").build();

    public static final Relationship FAIL_RELATIONSHIP = new Relationship.Builder().name("failure").description("HL7 data conversion failed").build();

    public static final Relationship HL7_NOT_DETECTED_RELATIONSHIP = new Relationship.Builder().name("HL7 data not detected").description("HL7 data not detected").build();

    public static final String APPLICATION_JSON = "application/json";

    private List<PropertyDescriptor> descriptors;

    private Set<Relationship> relationships;

    /**
     * Initialize the processor's properties and relationships
     * 
     * @param context
     *            the processor context
     */
    @Override
    protected void init(final ProcessorInitializationContext context) {
        final List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
        this.descriptors = Collections.unmodifiableList(descriptors);

        final Set<Relationship> relationships = new HashSet<Relationship>();
        relationships.add(SUCCESS_RELATIONSHIP);
        relationships.add(HL7_NOT_DETECTED_RELATIONSHIP);
        relationships.add(FAIL_RELATIONSHIP);
        this.relationships = Collections.unmodifiableSet(relationships);
    }

    /**
     * This method returns the relationships that have been defined
     * 
     * @return a set of relationships for this processor
     */
    @Override
    public Set<Relationship> getRelationships() {
        return this.relationships;
    }

    /**
     * This method returns the properties that have been defined
     * 
     * @return a list of properties
     */
    @Override
    public final List<PropertyDescriptor> getSupportedPropertyDescriptors() {
        return descriptors;
    }

    @OnScheduled
    public void onScheduled(final ProcessContext context) {
    }

    /**
     * This method will be called when it is scheduled to be run or when work exists in the form of flowfiles present on the input queue
     *
     * @param context
     *            information about how the processor is currently configured
     * @param session
     *            provides a mechanism to get and create/put flowfiles
     * @throws ProcessException
     */

    @Override
    public void onTrigger(final ProcessContext context, final ProcessSession session) throws ProcessException {
        FlowFile inputFlowFile = session.get();
        if (inputFlowFile == null) {
            return; // if there is no flowfile present then stop
        }

        getLogger().info("Reading text data from FlowFile");
        
        AtomicReference<String> uploadDataRate = new AtomicReference<String>();
        AtomicLong uploadMillis = new AtomicLong();        
        final StopWatch stopWatch = new StopWatch(true);
        AtomicReference<String> callBackMessage = new AtomicReference<String>();
        
        session.read(inputFlowFile, new InputStreamCallback() {
          /*
           * (non-Javadoc)
           * 
           * @see org.apache.nifi.processor.io.InputStreamCallback#process(java.io.InputStream)
           */
          @Override
          public void process(InputStream in) throws IOException {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(in))) {
              StringBuilder sb = new StringBuilder();
              String line = null;
              while ((line = reader.readLine()) != null) {
                sb.append(line + "\n");
              }
              callBackMessage.set(sb.toString());
              stopWatch.stop();
              uploadMillis.set(stopWatch.getDuration(TimeUnit.MILLISECONDS));
              uploadDataRate.set(stopWatch.calculateDataRate(inputFlowFile.getSize()));
            } catch (IOException e) {
              getLogger().error("Error reading flowfile", e);
              session.transfer(inputFlowFile, FAIL_RELATIONSHIP);
              return;
           }
          }
        });

        getLogger().info("Successfully read input data in {} at a rate of {}",
            new Object[] {
                FormatUtils.formatMinutesSeconds(uploadMillis.get(), TimeUnit.MILLISECONDS),
                uploadDataRate.get()});

        String inputMessage = callBackMessage.get();
        if (inputMessage == null || inputMessage.length() == 0) {
            session.transfer(inputFlowFile, FAIL_RELATIONSHIP);
            return; // if the incoming data is empty then stop
        }

        try {
            new HL7HapiParser().getParser().parse(inputMessage.toString());
        } catch (HL7Exception e) {
            session.transfer(inputFlowFile, HL7_NOT_DETECTED_RELATIONSHIP);
            return; // if the input data can't be parsed as HL7 then stop
        }

        try {
          String hl7Message = inputMessage.toString();
          HL7ToFHIRConverter ftv = new HL7ToFHIRConverter();
          String fhirMessage = ftv.convert(hl7Message); // generated a FHIR output

          FlowFile outputFlowFile = session.clone(inputFlowFile);

          outputFlowFile = session.write(outputFlowFile, new OutputStreamCallback() {
            /*
             * (non-Javadoc)
             * 
             * @see org.apache.nifi.processor.io.OutputStreamCallback#process(java.io.OutputStream)
             */
            @Override
            public void process(OutputStream out) throws IOException {
              try (OutputStream outputStream = new BufferedOutputStream(out)) {
                outputStream.write(fhirMessage.getBytes(StandardCharsets.UTF_8));
              } catch (IOException e) {
                getLogger().error("Error writing FHIR message to output flow", e);
                session.transfer(inputFlowFile, FAIL_RELATIONSHIP);
                return; // if the input data can't be parsed as HL7 then stop
              }
            }
          });

          session.putAttribute(outputFlowFile, CoreAttributes.MIME_TYPE.key(), APPLICATION_JSON);
          session.transfer(outputFlowFile, SUCCESS_RELATIONSHIP);
          session.remove(inputFlowFile); // remove the original flow file and stop
          getLogger().info("Pass FHIR flowfile to success queue");
        } catch (UnsupportedOperationException | IllegalArgumentException e) {
          getLogger().error("Error converting HL7 data to FHIR", e);
          session.transfer(inputFlowFile, FAIL_RELATIONSHIP);
          return; // if the input data can't be converted to FHIR then stop
        }
      }
}