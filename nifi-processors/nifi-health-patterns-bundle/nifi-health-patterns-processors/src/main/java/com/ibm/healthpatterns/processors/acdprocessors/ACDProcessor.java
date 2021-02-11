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
package com.ibm.healthpatterns.processors.acdprocessors;

import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.util.StandardValidators;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Base64.Encoder;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.net.ssl.HttpsURLConnection;

/**
 * This custom nifi processor is a simple ACD handler that will take a string of text and
 * via a call to acd, create flowfiles corresponding to any resources (medications or procedures)
 * that are found in the response.
 *
 * The incoming flowfile contains the raw text
 * The outgoing flowfiles contain the extracted JSON data for each resource
 *
 */
@Tags({"acd", "nlp", "ibm", "alvearie"})
public class ACDProcessor extends AbstractProcessor {

    // constants for resource property
    public static String MEDICATION = "medication";
    public static String PROCEDURE = "procedure";

    // constants for json response parsing
    public static String UNSTRUCTURED = "unstructured";
    public static String DATA = "data";
    public static String MEDICATIONIND = "MedicationInd";
    public static String PROCEDUREIND = "ProcedureInd";

    // constants for validity checking of json resource
    public static String DISAMBIGUATION_DATA = "disambiguationData";
    public static String VALIDITY = "validity";
    public static String VALID = "valid";
    public static String NO_DECISION = "NO_DECISION";

    /**
     * This nifi processor will have four properties that need to be configured by the user
     *
     * ACD_URL_PROPERTY defines acdURL: the location of the ACD service to be called
     * ACD_USERNAME_PROPERTY defines acdUser: the username will default to apikey
     * ACD_SECRET_PROPERTY defines acdSecret: the provided apikey (will be hidden when entered in the processor)
     * ACD_RESOURCES_PROPERTY defines acdResources the resources that will be extracted from the acd response
     *                         a pipe "|" delimited string with values
     *                         medication or procedure or both
     *                         for example medication|procedure
     */
    public static final PropertyDescriptor ACD_URL_PROPERTY = new PropertyDescriptor
            .Builder().name("acdURL")
            .displayName("ACD URL")
            .description("Endpoint for the ACD service")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor ACD_USERNAME_PROPERTY = new PropertyDescriptor
            .Builder().name("acdUser")
            .displayName("ACD Username")
            .description("Username for the ACD service-default to apikey")
            .required(true)
            .defaultValue("apikey")
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    public static final PropertyDescriptor ACD_SECRET_PROPERTY = new PropertyDescriptor
            .Builder().name("acdSecret")
            .displayName("ACD Secret")
            .description("Secret (apikey) for the ACD service")
            .required(true)
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .sensitive(true)
            .build();

    public static final PropertyDescriptor ACD_RESOURCES_PROPERTY = new PropertyDescriptor
            .Builder().name("acdResources")
            .displayName("ACD Resources")
            .required(true)
            .description("Resources to extract from ACD response (medication|procedure)")
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();

    /**
     * This nifi processor will have two relationships
     * SUCCESS: the processing occurred without error
     * FAIL: the processing terminated with an error
     *       the original flowfile is passed on to the fail relationship
     *
     */
    public static final Relationship SUCCESS_RELATIONSHIP = new Relationship.Builder()
            .name("Success")
            .description("Text was processed successfully")
            .build();

    public static final Relationship FAIL_RELATIONSHIP = new Relationship.Builder()
            .name("Failure")
            .description("Text processing failed")
            .build();

    private List<PropertyDescriptor> descriptors;
    private Set<Relationship> relationships;

    /**
     * Initialize the processor with the four properties and two relationships defined above
     * @param context the processor context
     */
    @Override
    protected void init(final ProcessorInitializationContext context) {
        final List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
        descriptors.add(ACD_URL_PROPERTY);
        descriptors.add(ACD_USERNAME_PROPERTY);
        descriptors.add(ACD_SECRET_PROPERTY);
        descriptors.add(ACD_RESOURCES_PROPERTY);
        this.descriptors = Collections.unmodifiableList(descriptors);

        final Set<Relationship> relationships = new HashSet<Relationship>();
        relationships.add(SUCCESS_RELATIONSHIP);
        relationships.add(FAIL_RELATIONSHIP);
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

    @OnScheduled
    public void onScheduled(final ProcessContext context) {

    }

    /**
     * This method will be called when it is scheduled to be run or when work exists in the form
     * of flowfiles present on the input queue
     *
     * @param context information about how the processor is currently configured
     * @param session provides a mechanism to get and create/put flowfiles
     *
     * @throws ProcessException
     */
    @Override
    public void onTrigger(final ProcessContext context, final ProcessSession session) throws ProcessException {
        FlowFile flowFile = session.get();
        if ( flowFile == null ) {
            return; //if there is no flowfile present then stop
        }

        getLogger().info("Reading text data from FlowFile");
        InputStream is = session.read(flowFile);
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));

        String docData = null;

        try {
            docData = reader.readLine();
            reader.close();
        } catch (IOException ioe) {

        }

        if (docData == null || docData.length() == 0) {
            session.transfer(flowFile, FAIL_RELATIONSHIP);
            return; //if the incoming data is empty then stop
        }

        String resourcesRequested = context.getProperty(ACD_RESOURCES_PROPERTY).getValue();
        if (resourcesRequested == null || resourcesRequested.length() == 0) {
            session.transfer(flowFile, FAIL_RELATIONSHIP);
            getLogger().info("No resources were requested");
            return; //if the resource string is not present then stop
        }

        try {
            URL acdURL = new URL(context.getProperty(ACD_URL_PROPERTY).getValue());
            HttpsURLConnection acdConnection = (HttpsURLConnection) acdURL.openConnection();

            // Basic authentication requires base 64 encoding of the username and password
            String authACD = context.getProperty(ACD_USERNAME_PROPERTY).getValue()
                    + ":" + context.getProperty(ACD_SECRET_PROPERTY).getValue();
            Encoder acdEncoder = Base64.getEncoder();
            String acdEncodedString = acdEncoder.encodeToString(authACD.getBytes());
            String acdAuthHeaderValue = "Basic " + acdEncodedString;
            acdConnection.setRequestProperty("Authorization", acdAuthHeaderValue);

            // The input text string will be sent to ACD with a POST request
            // The response will be a json string

            acdConnection.setRequestMethod("POST");
            acdConnection.setRequestProperty("Content-Type","text/plain");
            acdConnection.setRequestProperty("Accept", "application/json");
            acdConnection.setRequestProperty("User-Agent","");

            acdConnection.setDoOutput(true);

            getLogger().info("Calling ACD service");
            try(OutputStream os = acdConnection.getOutputStream()) {
                byte[] body = docData.getBytes("utf-8");
                os.write(body, 0, body.length);
            } catch (Exception e) {
                session.transfer(flowFile, FAIL_RELATIONSHIP);  //if there is an error in the ACD transaction
                getLogger().info("Error in calling ACD service");
                return;
            }

            getLogger().info("ACD Response code/message " + acdConnection.getResponseCode() + acdConnection.getResponseMessage());

            // if the request succeeds, parse out the resources as requested in the properties and
            // create flowfiles to be passed to the success relationship
            if (acdConnection.getResponseCode() == HttpURLConnection.HTTP_OK) { // success on ACD call
                String acdResponseString = null;
                try (BufferedReader acdIn = new BufferedReader(new InputStreamReader(
                        acdConnection.getInputStream()))) {

                    StringBuilder acdResponse = new StringBuilder();

                    String acdInputLine;
                    while ((acdInputLine = acdIn.readLine()) != null) {
                        acdResponse.append(acdInputLine);
                    }
                    acdIn.close();
                    getLogger().info("Good ACD response " + acdResponse.toString());

                    acdResponseString = acdResponse.toString();
                } catch (Exception e) {
                    acdResponseString = null;
                }

                if (acdResponseString != null) {

                    // parse out the json to find medications and procedures
                    // build flow file for each
                    // Note: json structured could be different for each type of resource

                    // first extract medications if desired
                    if (resourcesRequested.toLowerCase().contains(MEDICATION)) {
                        JSONArray medJson = parseMedications(acdResponseString);

                        if (medJson != null) {
                            for (Object med:medJson) {
                                if (isValid((JSONObject) med)) {
                                    FlowFile f = session.clone(flowFile);

                                    getLogger().info("Writing data to new flowfile" + med.toString());
                                    OutputStream newFlowOutput = session.write(f);
                                    newFlowOutput.write(med.toString().getBytes());
                                    newFlowOutput.close();

                                    session.transfer(f, SUCCESS_RELATIONSHIP);
                                    getLogger().info("Pass medication flowfile to success queue");
                                }
                            }
                        }
                    }

                    // second extract procedures if desired
                    if (resourcesRequested.toLowerCase().contains(PROCEDURE)) {
                        JSONArray procJson = parseProcedures(acdResponseString);
                        if (procJson != null) {
                            for (Object proc:procJson) {
                                if (isValid((JSONObject) proc)) {
                                    FlowFile f = session.clone(flowFile);

                                    getLogger().info("Writing data to new flowfile" + proc.toString());
                                    OutputStream newFlowOutput = session.write(f);
                                    newFlowOutput.write(proc.toString().getBytes());
                                    newFlowOutput.close();

                                    session.transfer(f, SUCCESS_RELATIONSHIP);
                                    getLogger().info("Pass procedure flowfile to success queue");
                                }
                            }
                        }
                    }
                } else {
                    session.transfer(flowFile, FAIL_RELATIONSHIP);
                    getLogger().info("Pass flow file to failure due to bad ACD request");
                    return;
                }

                session.remove(flowFile);  //remove the original flow file and stop
                return;
            } else {
                StringBuilder acdResponse = null;
                try (BufferedReader acdIn = new BufferedReader(new InputStreamReader(
                        acdConnection.getInputStream()))) {

                    acdResponse = new StringBuilder();
                    String acdInputLine;
                    while ((acdInputLine = acdIn.readLine()) != null) {
                        acdResponse.append(acdInputLine);
                    }
                    acdIn.close();

                    getLogger().info("Bad ACD response " + acdResponse.toString());
                    session.transfer(flowFile, FAIL_RELATIONSHIP);
                    return;
                } catch (Exception e) {
                    getLogger().info("Bad ACD response " + acdResponse.toString());
                    session.transfer(flowFile, FAIL_RELATIONSHIP);
                    return;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            session.transfer(flowFile, FAIL_RELATIONSHIP);
            return;
        }
    }

    /**
     * This method will return true if the json response for a particular resource is considered
     * 'valid'
     * @param item the json resource extracted from the resonse
     * @return true if resource is ok to use
     *         false otherwise
     */
    private static boolean isValid(JSONObject item) {
        boolean validData = false;

        JSONObject ambData = (JSONObject) item.get(DISAMBIGUATION_DATA);
        if (ambData != null) {
            String validity = (String) ambData.get(VALIDITY);
            if (validity != null && (validity.equalsIgnoreCase(VALID)
                    || validity.equalsIgnoreCase(NO_DECISION))) {
                validData = true;
            }
        }

        return validData;
    }

    /**
     * This method will parse out the medications found in the acd response
     * @param acdResponseString
     * @return Array of medications, null if there is a problem
     */
    private static JSONArray parseMedications(String acdResponseString) {
        try {
            Object obj = new JSONParser().parse(acdResponseString);
            JSONObject acdJson = (JSONObject) obj;

            JSONArray mainACDJson = (JSONArray) acdJson.get(UNSTRUCTURED);
            JSONObject initialACDJson = (JSONObject) mainACDJson.get(0);
            JSONObject dataJson = (JSONObject) initialACDJson.get(DATA);
            JSONArray medJson = (JSONArray) dataJson.get(MEDICATIONIND);
            return medJson;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * This method will parse out the procedures found in the acd response
     * @param acdResponseString
     * @return Array of procedures, null if there is a problem
     */
    private static JSONArray parseProcedures(String acdResponseString) {
        try {
            Object obj = new JSONParser().parse(acdResponseString);
            JSONObject acdJson = (JSONObject) obj;

            JSONArray mainACDJson = (JSONArray) acdJson.get(UNSTRUCTURED);
            JSONObject initialACDJson = (JSONObject) mainACDJson.get(0);
            JSONObject dataJson = (JSONObject) initialACDJson.get(DATA);
            JSONArray procJson = (JSONArray) dataJson.get(PROCEDUREIND);
            return procJson;
        } catch (Exception e) {
            return null;
        }
    }

}
