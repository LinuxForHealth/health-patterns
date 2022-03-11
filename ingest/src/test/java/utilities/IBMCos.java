package utilities;

import com.ibm.cloud.objectstorage.ClientConfiguration;
import com.ibm.cloud.objectstorage.auth.AWSCredentials;
import com.ibm.cloud.objectstorage.auth.AWSStaticCredentialsProvider;
import com.ibm.cloud.objectstorage.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.ibm.cloud.objectstorage.services.s3.AmazonS3;
import com.ibm.cloud.objectstorage.services.s3.AmazonS3ClientBuilder;
import com.ibm.cloud.objectstorage.services.s3.model.Bucket;
import com.ibm.cloud.objectstorage.services.s3.model.GetObjectRequest;
import com.ibm.cloud.objectstorage.services.s3.model.ListObjectsRequest;
import com.ibm.cloud.objectstorage.services.s3.model.ObjectListing;
import com.ibm.cloud.objectstorage.services.s3.model.S3Object;
import com.ibm.cloud.objectstorage.services.s3.model.S3ObjectSummary;
import com.ibm.cloud.objectstorage.oauth.BasicIBMOAuthCredentials;

import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;



public class IBMCos {
	
	private String bucketName;
	private String apiKey;
	private String serviceInstanceId;
	private String endpointUrl;
	private String location;
	private String itemName;
	private String findString;
	private AmazonS3 cosClient;
	Map<String, String> outMap;
	
    public IBMCos( Map<String, String> in ) {
    	this.bucketName = in.get("bucketName");
        this.apiKey = in.get("apiKey");
        this.serviceInstanceId = in.get("serviceInstanceId");
        this.endpointUrl = in.get("endpointUrl");
        this.location = in.get("location");
        this.itemName = in.get("itemName");
        this.findString = in.get("findString");
        this.cosClient = createClient(this.apiKey, this.serviceInstanceId, this.endpointUrl, this.location);
        System.out.println(this.cosClient.toString());
        outMap = new HashMap<String, String>();
    }

   
    
    public static AmazonS3 createClient(String apiKey, String serviceInstanceId, String endpointUrl, String location)
    {
        AWSCredentials credentials = new BasicIBMOAuthCredentials(apiKey, serviceInstanceId);
        ClientConfiguration clientConfig = new ClientConfiguration()
                .withRequestTimeout(5000)
                .withTcpKeepAlive(true);

        return   AmazonS3ClientBuilder
                .standard()
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .withEndpointConfiguration(new EndpointConfiguration(endpointUrl, location))
                .withPathStyleAccessEnabled(true)
                .withClientConfiguration(clientConfig)
                .build();
    }

    public void listObjects()
    {
        System.out.println("Listing objects in bucket " + bucketName);

        try {
            ObjectListing objectListing = cosClient.listObjects(new ListObjectsRequest().withBucketName(bucketName));
            for (S3ObjectSummary objectSummary : objectListing.getObjectSummaries()) {
                System.out.println(" - " + objectSummary.getKey() + "  " + "(size = " + objectSummary.getSize() + ")");
            }  	
        }
        catch(Exception e) {
        	System.out.println(e.toString());
        }

        System.out.println();
        
    }


    public Map<String, String> listBuckets()
    {
    
    	String tempBucket = "";
        System.out.println("Listing buckets");
        
        try {
             List<Bucket> bucketList = cosClient.listBuckets();
            for (Bucket bucket : bucketList) {
                System.out.println(bucket.getName());
                System.out.println("temp Bucket = '"+tempBucket+"'");
                System.out.println("bucketName = '"+bucketName+"'");
                outMap.put(bucketName, tempBucket+","+bucket.getName());
                tempBucket = outMap.get(bucketName);              
            }	
        }
        catch(Exception e) {
        	System.out.println(e.toString());
        }

        System.out.println();
        
        return outMap;
    }
    
    public Map<String, String> getItem() {
        System.out.printf("Retrieving item from bucket: %s, key: %s\n", bucketName, itemName);

        S3Object item = cosClient.getObject(new GetObjectRequest(bucketName, itemName));

        outMap.put("result","false");
        
        try {
            final int bufferSize = 1024;
            final char[] buffer = new char[bufferSize];
            final StringBuilder out = new StringBuilder();
            InputStreamReader in = new InputStreamReader(item.getObjectContent());

            for (; ; ) {
                int rsz = in.read(buffer, 0, buffer.length);
                if (rsz < 0)
                    break;
                out.append(buffer, 0, rsz);
            }

            System.out.println(out.toString());
                       
            if(out.toString().contains(findString)) {
            	outMap.put("result","true");
            }
            
            
        } catch (IOException ioe){
            System.out.printf("Error reading file %s: %s\n", itemName, ioe.getMessage());
        }
        
        return outMap;
    }
    
}
