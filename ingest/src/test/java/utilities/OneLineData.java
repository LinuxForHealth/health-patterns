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


public class OneLineData {

    private String fileIn;
	private boolean result;

    @JsonCreator
    public OneLineData(
    		@JsonProperty("fileIn")String fileIn,
    		@JsonProperty("result")boolean result) {
        this.fileIn = fileIn;
        this.result = true;
    }
    
    public String getFileIn() {
    	return fileIn;
    }
    
    public boolean getResult() {
        return result;
    }

    public void setResult(boolean newResult) {
    	result = newResult;
    }

    
}
