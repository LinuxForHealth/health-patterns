# Configure nlp-insights to use QuickUMLS for NLP
Once nlp-insights has been configured to use QuickUMLS, it will use the QuickUMLS service for it's NLP operations by default.

## Start the nlp-insights service
If the nlp-insights service has not been started, follow the directions [here](../setup/start_nlp_insights.md) to start the server in a local container.

## Create a configuration for QuickUMLS
The first step is to create the definition for the QuickUMLS service. Replace `<service_url_here>` with your endpoint.

```
curl -w "%{http_code}\n" -o - -XPOST localhost:5000/config/definition  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
  "name": "quickconfig1",
  "nlpServiceType": "quickumls",
  "config": {
    "endpoint": "https://<service_url_here>/match"
  }
}
EOF
```

<details><summary>output</summary>

200

</details>


## Set QuickUmls as the default configuration
Now the definition of the QuickUMLS service exists, we can set it as the default service. You should  be aware that this operation affects all users of the nlp-insights service.

```
curl -w "\n%{http_code}\n" -o - -XPOST localhost:5000/config/setDefault?name=quickconfig1
```

<details><summary>output</summary>

Default config set to: quickconfig1

200
</details>

## Configuring at deploy time
In some environments (such as k8s), it may be necessary to configure the server at deploy time, rather than with a REST API. Instructions for how to do that is located [here](../../developer/kubernetes.md).