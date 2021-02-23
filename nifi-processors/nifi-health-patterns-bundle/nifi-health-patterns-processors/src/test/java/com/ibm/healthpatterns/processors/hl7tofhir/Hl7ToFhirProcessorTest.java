/*
 * Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements. See the NOTICE file distributed with this work for additional information regarding copyright
 * ownership. The ASF licenses this file to You under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the
 * License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
 */
package com.ibm.healthpatterns.processors.hl7tofhir;

import static org.junit.Assert.assertTrue;

import java.util.List;
import org.apache.nifi.flowfile.attributes.CoreAttributes;
import org.apache.nifi.util.MockFlowFile;
import org.apache.nifi.util.TestRunner;
import org.apache.nifi.util.TestRunners;
import org.junit.Before;
import org.junit.Test;

/**
 * This class can be used to run your processor locally. If you wish to do development, it is suggested that you add functionality to the testProcessor() class run exercise your processor via a test
 * execution.
 */
public class Hl7ToFhirProcessorTest {

    private TestRunner testRunner;

    @Before
    public void init() {
        testRunner = TestRunners.newTestRunner(HL7ToFhirProcessor.class);
    }

    @Test
    public void testProcessor() {
        String content = "MSH|^~\\&|SE050|050|PACS|050|20120912011230||ADT^A01|102|T|2.6|||AL|NE\n" + "EVN||201209122222\n"
                + "PID|0010||PID1234^5^M11^A^MR^HOSP~1234568965^^^USA^SS||DOE^JOHN^A^||19800202|F||W|111 TEST_STREET_NAME^^TEST_CITY^NY^111-1111^USA||(905)111-1111|||S|ZZ|12^^^124|34-13-312||||TEST_BIRTH_PLACE\n"
                + "PV1|1|ff|yyy|EL|ABC||200^ATTEND_DOC_FAMILY_TEST^ATTEND_DOC_GIVEN_TEST|201^REFER_DOC_FAMILY_TEST^REFER_DOC_GIVEN_TEST|202^CONSULTING_DOC_FAMILY_TEST^CONSULTING_DOC_GIVEN_TEST|MED|||||B6|E|272^ADMITTING_DOC_FAMILY_TEST^ADMITTING_DOC_GIVEN_TEST||48390|||||||||||||||||||||||||201409122200|\n"
                + "OBX|1|TX|1234||ECHOCARDIOGRAPHIC REPORT||||||F|||||2740^TRDSE^Janetary~2913^MRTTE^Darren^F~3065^MGHOBT^Paul^J~4723^LOTHDEW^Robert^L|\r\n"
                + "AL1|1|DRUG|00000741^OXYCODONE||HYPOTENSION\n" + "AL1|2|DRUG|00001433^TRAMADOL||SEIZURES~VOMITING\r\n" + "PRB|AD|200603150625|aortic stenosis|53692||2||200603150625";
        // Add the content to the runner
        testRunner.enqueue(content);

        // Run the enqueued content, it also takes an int = number of contents queued
        testRunner.run(1);

        // All results were processed with out failure
        testRunner.assertQueueEmpty();

        List<MockFlowFile> flowFiles = testRunner.getFlowFilesForRelationship("success");
        assertTrue("No Flow Files returned on success relationship", flowFiles != null && flowFiles.size() == 1);

        MockFlowFile flowFile = flowFiles.get(0);
        String data = new String(flowFile.getData());
        assertTrue("HL7 data not converted correctly", data != null && data.startsWith("{"));
        
        flowFile.assertAttributeEquals(CoreAttributes.MIME_TYPE.key(), HL7ToFhirProcessor.APPLICATION_JSON);
    }
}
