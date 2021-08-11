/*******************************************************************************
 * Java Class for Zerocode
 * 
 * Zerocode Structure for performing string functions not available in Zerocode
 *******************************************************************************/
package utilities;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Objects;

public class ZerocodeString {
    private String string1;
    private String string2;
    private String result;

    @JsonCreator
    public ZerocodeString(
    		@JsonProperty("result")String result,
            @JsonProperty("string1")String string1,
            @JsonProperty("string2")String string2) {
    	this.string1 = string1;
        this.string2 = string2;
        this.result = "";
    }

    public String getString1() {
        return string1;
    }

    public String getString2() {
        return string2;
    }

    public String getResult() {
        return result;
    }
    
    public void setString1(String str) {
    	this.string1 = str;
    }
    
    public void setString2(String str) {
    	this.string2 = str;
    }
    
    public void setResult(String newResult) {
        this.result = newResult;
    }

}
