/*******************************************************************************
 * Java CLass for Zerocode
 * 
 * Zerocode Structure for comparing two specific strings
 *******************************************************************************/
package utilities;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Objects;

public class PriDeIDCompare {
    private String priString;
    private String deidString;
    private String dataName;
    private boolean result;

    @JsonCreator
    public PriDeIDCompare(
    		@JsonProperty("result")boolean result,
    		@JsonProperty("dataName")String dataName,
            @JsonProperty("pri")String priString,
            @JsonProperty("deid")String deidString) {
        this.dataName = dataName;
    	this.priString = priString;
        this.deidString = deidString;
        this.result = true;
    }

    public String getDeidString() {
        return deidString;
    }

    public String getPriString() {
        return priString;
    }

    public String getDataName() {
        return dataName;
    }
    
    public boolean getResult() {
        return result;
    }
    
    public void setResult(boolean newResult) {
        this.result = newResult;
    }

    @Override
    public String toString() {
        return dataName+" Strings Compared {" +
                "pri ='" + priString +
                "', deid='" + deidString +"'}";
         
    }
}
