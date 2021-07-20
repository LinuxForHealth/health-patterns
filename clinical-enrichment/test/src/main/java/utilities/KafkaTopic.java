/*******************************************************************************
 * IBM Confidential OCO Source Materials
 * 5737-D31, 5737-A56
 * (C) Copyright IBM Corp. 2020, 2021
 *
 * The source code for this program is not published or otherwise
 * divested of its trade secrets, irrespective of what has
 * been deposited with the U.S. Copyright Office.
 *******************************************************************************/
package utilities;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

/****************************************************************************/
/* This class has not been used, and is not tested.   It is being included  */
/* as a reference in case it is needed in the future.                       */
/****************************************************************************/

public class KafkaTopic {

    private String topicMessages;
    private String lastMessage;

    @JsonCreator
    public KafkaTopic(
    		@JsonProperty("topicMessages")String topicMessages,
    		@JsonProperty("lastMessage") String lastMessage,
    		@JsonProperty("result")boolean result) {
        this.topicMessages = topicMessages;
        this.lastMessage = "";
    }
    
    public String getTopicMessages() {
    	return topicMessages;
    }
    
    public void setLastMessage() {
    	int lMEnd = topicMessages.lastIndexOf("Message: ConsumerRecord");
    	int lMStart = topicMessages.substring(0, lMEnd).lastIndexOf("Message: ConsumerRecord");
    	lastMessage =  topicMessages.substring(lMStart,lMEnd);
    }
    
    public String getLastMessage() {
    	return lastMessage;
    }
    
}
