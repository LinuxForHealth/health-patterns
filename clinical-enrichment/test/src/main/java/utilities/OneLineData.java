/*******************************************************************************
 * Java Class for Zerocode
 * 
 * Data object for removing newline chars from a file
 * 
 * This class has not been used, and is not tested.   It is being included  
 * as a reference in case it is needed in the future.
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
