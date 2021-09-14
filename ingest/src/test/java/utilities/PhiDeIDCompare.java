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

import java.util.Objects;

public class PhiDeIDCompare {
    private String phiString;
    private String deidString;
    private String dataName;
    private boolean result;

    @JsonCreator
    public PhiDeIDCompare(
    		@JsonProperty("result")boolean result,
    		@JsonProperty("dataName")String dataName,
            @JsonProperty("phi")String phiString,
            @JsonProperty("deid")String deidString) {
        this.dataName = dataName;
    	this.phiString = phiString;
        this.deidString = deidString;
        this.result = true;
    }

    public String getdeidString() {
        return deidString;
    }

    public String getphiString() {
        return phiString;
    }

    public String getdataName() {
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
                "phi ='" + phiString +
                "', deid='" + deidString +"'}";
         
    }
}
