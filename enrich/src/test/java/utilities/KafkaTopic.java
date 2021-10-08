/*******************************************************************************
 * Java Class for Zerocode
 *  Kafka topic structure as serviced by expose-kafka
 *  
 * This class has not been used, and is not tested.   It is being included
 * as a reference in case it is needed in the future. 
 *******************************************************************************/
package utilities;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

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
