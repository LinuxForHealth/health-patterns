# OUTPUT OBSOLETE 

# Configure nlp-insights to use ACD for NLP
Once nlp-insights has been configured to use ACD, it will use the ACD 
service for it's NLP operations by default.

## Start the nlp-insights service
If the nlp-insights service has not been started, follow the directions [here](../setup/start_nlp_insights.md) to start the server in a local container.

## Create a configuration for ACD
The first configuration step is to create the definition for the ACD service. Replace `<your_api_key_here>` with the key for your instance. You can find the api key by opening your service from the IBM Cloud resource list and navigating to "service credentials". The nlp-insights service needs at least reader authority.

Check that the endpoint is correct for your service.

The nlp-insights service is designed for the out of the box wh_acd.ibm_clinical_insights_v1.0_standard_flow. Customized flows may require modification of the source code in order to fully leverage the customizations.

```
curl -w "%{http_code}\n" -o - -XPOST localhost:5000/config/definition  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
  "name": "acdconfig1",
  "nlpServiceType": "acd",
  "config": {
    "apikey": <your-api-key-here>,
    "endpoint": "https://us-east.wh-acd.cloud.ibm.com/wh-acd/api",
    "flow": "wh_acd.ibm_clinical_insights_v1.0_standard_flow"
  }
}
EOF
```

<details><summary>output</summary>

200

</details>


## Set ACD as the default configuration
Now the definition of the ACD service exists, we can set it as the default service. You should  be aware that this operation affects all users of the nlp-insights service.

```
curl -w "\n%{http_code}\n" -o - -XPOST localhost:5000/config/setDefault?name=acdconfig1
```

<details><summary>output</summary>

Default config set to: acdconfig1

200

</details>
