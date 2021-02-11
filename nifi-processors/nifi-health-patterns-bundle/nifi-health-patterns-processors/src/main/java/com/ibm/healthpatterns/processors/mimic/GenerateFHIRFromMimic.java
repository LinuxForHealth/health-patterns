/*
 * Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements. See the NOTICE file distributed with this work for additional information regarding copyright
 * ownership. The ASF licenses this file to You under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the
 * License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
 */
package com.ibm.healthpatterns.processors.mimic;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.nifi.annotation.behavior.InputRequirement;
import org.apache.nifi.annotation.behavior.InputRequirement.Requirement;
import org.apache.nifi.annotation.behavior.SupportsBatching;
import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.annotation.lifecycle.OnStopped;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.io.OutputStreamCallback;
import org.apache.nifi.processor.util.StandardValidators;

import de.uzl.itcr.mimic2fhir.Mimic2Fhir2;
import de.uzl.itcr.mimic2fhir.work.Config;

/**
 * This NIFI Processor will read from a Mimic database defined by the supplied parameters, and generate one FHIR bundle per patient, containing all relevant data found in MIMIC. This will be supplied
 * as a flowfile to be used in NIFI.
 * 
 * @author AdamClark
 */
@SupportsBatching
@Tags({"fhir", "mimic", "ibm", "alvearie"})
@InputRequirement(Requirement.INPUT_FORBIDDEN)
@CapabilityDescription("This processor creates FlowFiles with FHIR resources, based on the current data stored in the target Mimic database")
public class GenerateFHIRFromMimic extends AbstractProcessor {

    public static final PropertyDescriptor MIMIC_DB_NAME = new PropertyDescriptor.Builder()
            .displayName("Mimic DB Name")
            .name("mimic-db-name")
            .description("Mimic Database name to use")
            .defaultValue("mimic")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor MIMIC_PASSWORD = new PropertyDescriptor.Builder()
            .displayName("Mimic DB Password")
            .name("mimic-password")
            .description("Password to use for connecting to Mimic DB Server")
            .defaultValue("mimic_passw0rd")
            .sensitive(true)
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor MIMIC_PORT = new PropertyDescriptor.Builder()
            .displayName("Mimic DB Port")
            .name("mimic-port")
            .description("Mimic DB Server port")
            .defaultValue("5432")
            .required(true)
            .addValidator(StandardValidators.PORT_VALIDATOR)
            .build();

    public static final PropertyDescriptor MIMIC_SCHEMA = new PropertyDescriptor.Builder()
            .displayName("Mimic DB Schema")
            .name("mimic-schema")
            .description("Mimic Database Schema to use")
            .defaultValue("mimic")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor MIMIC_SERVER = new PropertyDescriptor.Builder()
            .displayName("Mimic DB Server")
            .name("mimic-db-server")
            .description("Mimic DB Server containing data to be converted to FHIR")
            .defaultValue("mimic-db-server")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor MIMIC_USER = new PropertyDescriptor.Builder()
            .displayName("Mimic DB User")
            .name("mimic-user")
            .description("User to use for connecting to Mimic DB Server")
            .defaultValue("mimic_user")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final Relationship SUCCESS = new Relationship.Builder().name("success").build();

    public static final String VERSION = "GenerateFHIRFromMimic V0.0.1";

    private List<PropertyDescriptor> descriptors;

    private Mimic2Fhir2 mimic2Fhir;

    private AtomicInteger patientCounter = new AtomicInteger(0);

    private Set<Relationship> relationships;

    private String getNextPatient() {
        String nextPatient = mimic2Fhir.getNextPatient();
        if (nextPatient != null) {
            patientCounter.incrementAndGet();
        }
        return nextPatient;
    }

    @Override
    public Set<Relationship> getRelationships() {
        return relationships;
    }

    @Override
    protected List<PropertyDescriptor> getSupportedPropertyDescriptors() {
        return descriptors;
    }

    /*
     * Initialize the processor descriptors/relationships
     */
    @Override
    protected void init(final ProcessorInitializationContext context) {
        final List<PropertyDescriptor> descriptors = new ArrayList<>();
        descriptors.add(MIMIC_SERVER);
        descriptors.add(MIMIC_PORT);
        descriptors.add(MIMIC_USER);
        descriptors.add(MIMIC_PASSWORD);
        descriptors.add(MIMIC_DB_NAME);
        descriptors.add(MIMIC_SCHEMA);
        this.descriptors = Collections.unmodifiableList(descriptors);

        final Set<Relationship> relationships = new HashSet<>();
        relationships.add(SUCCESS);
        this.relationships = Collections.unmodifiableSet(relationships);

    }

    /*
     * This method will be called when the processor is first scheduled to run. It initializes connections to the configured Mimic DB.
     */
    @OnScheduled
    public final void onScheduled(final ProcessContext context) throws IOException {
        // Add server and config data..
        Config config = new Config();

        // Postgres
        config.setPostgresServer(context.getProperty(MIMIC_SERVER).getValue());
        config.setPortPostgres(context.getProperty(MIMIC_PORT).getValue());
        config.setUserPostgres(context.getProperty(MIMIC_USER).getValue());
        config.setPassPostgres(context.getProperty(MIMIC_PASSWORD).getValue());
        config.setDbnamePostgres(context.getProperty(MIMIC_DB_NAME).getValue());
        config.setSchemaPostgres(context.getProperty(MIMIC_SCHEMA).getValue());

        patientCounter = new AtomicInteger(0);
        mimic2Fhir = new Mimic2Fhir2();
        mimic2Fhir.setConfig(config);
        mimic2Fhir.start();
        getLogger().info("GenerateFHIRFromMimic scheduled to read from Mimic DB.");
    }

    @OnStopped
    public final void onStopped(final ProcessContext context) throws IOException {
        mimic2Fhir = null;
    }

    /*
     * This method will be called to create another flow file. If all records have been processed from the mimic server, or an error occurred, stop producing new flow files.
     */
    @Override
    public void onTrigger(final ProcessContext context, final ProcessSession session) {
        if (mimic2Fhir == null) {
            return;
        }
        FlowFile flowFile = null;
        try {
            String nextBundle = getNextPatient();
            if (nextBundle == null || nextBundle.isEmpty()) {
                mimic2Fhir = null;
                getLogger().info("GenerateFHIRFromMimic done reading from Mimic DB. Total patients read: " + patientCounter);
                return;
            }
            flowFile = session.create();
            final byte[] data = nextBundle.getBytes();
            flowFile = session.write(flowFile, new OutputStreamCallback() {
                @Override
                public void process(final OutputStream out) throws IOException {
                    out.write(data);
                }
            });
            session.getProvenanceReporter().create(flowFile);
            session.transfer(flowFile, SUCCESS);
        } catch (Throwable t) {
            getLogger().error("Error generating FHIR data from Mimic DB", t);
            if (flowFile != null) {
                session.remove(flowFile);
            }
            mimic2Fhir = null;
            throw t;
        }
    }
}