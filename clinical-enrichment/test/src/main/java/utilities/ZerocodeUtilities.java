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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDate;


public class ZerocodeUtilities {

	private boolean executeCMD(String cmd) {
		System.out.println("Command:'"+cmd+"' Execution:");
    	try {
        	Process process = Runtime.getRuntime().exec(cmd);
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line = "";
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
    	}
    	catch (Exception e )  { 
    		System.out.println("Command:'"+cmd+"' Failed with:");
    		System.out.println(e); 
    		return false;
    		}
    	return true;
	}
	
    
    public PriDeIDCompare notEqual(PriDeIDCompare pd) throws InterruptedException {
        
    	System.out.println("input object: "+pd.toString());
   	
    	String priStr = pd.getPriString();
    	String deidStr = pd.getDeidString();
    	
    	if(priStr.equals(deidStr)) {
    		pd.setResult(false);
    		System.out.println("PRIMARY FHIR and DEID FHIR data identical for "+pd.getDataName()+" ");
    	}
        
        return pd;
        
    }
    
    public ZerocodeString containsString(ZerocodeString zs) throws InterruptedException {
    	
    	if (zs.getString1().contains(zs.getString2())) {
    		zs.setResult("true");
    	}
    	else
    		zs.setResult("false");
    	
    	return zs;
    }
    
    public ZerocodeString getLastOccurenceDate(ZerocodeString zs)throws InterruptedException {
    	
    	if (zs.getString1().contains("occurrenceDateTime")) {
    		int dateStart = zs.getString1().lastIndexOf("occurrenceDateTime")+21;
    		int dateEnd = dateStart + 20;
    		
    		String dateString = zs.getString1().substring(dateStart,dateEnd);
    	    
    	    zs.setString2(dateString);
    	    zs.setResult("true");
    	}
    	else
    		zs.setResult("false");
    	
    	return zs;
    }
    
    public ZerocodeString stringEqual(ZerocodeString zs)throws InterruptedException {
    	
    	if (zs.getString1().equals(zs.getString2())) {

    		zs.setResult("true");
    	}
    	else
    		zs.setResult("false");
    	
    	return zs;
    }
    
    public ZerocodeString stringNotEqual(ZerocodeString zs)throws InterruptedException {
    	
    	if (zs.getString1().equals(zs.getString2())) {

    		zs.setResult("false");
    	}
    	else
    		zs.setResult("true");
    	
    	return zs;
    }
    
// Functions for delaying the test steps
    public void milliSecondsDelay(int milliSec) throws InterruptedException {
        Thread.sleep(milliSec);
    }

    public void secondsDelay(int seconds) throws InterruptedException {
        Thread.sleep(seconds*1000);
    }

    public void minutesDelay(int min) throws InterruptedException {
        Thread.sleep(min*60*1000);
    }
  
    
// Functions that have not been used and have not been tested.   Included in
// in case they are needed in the future.  
    
    public KafkaTopic getLastTopicMessage(KafkaTopic tk)  {
    	 	
    	tk.setLastMessage();
    	
    	System.out.println("Last Message:"+tk.getLastMessage());
    	
    	return tk;
    }
    
    public OneLineData makeOneLine(OneLineData ol) throws InterruptedException {
    	

    	String fileIn = ol.getFileIn();
   
    	
        if (executeCMD("chmod +x src/test/scripts/createSingleLineJSON.sh")) {
        	ol.setResult(executeCMD("src/test/scripts/createSingleLineJSON.sh "+fileIn));
        }
        else {
        	ol.setResult(false);
        }
    	
        return ol;
        
    }
	
}
