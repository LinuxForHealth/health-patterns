# Deploy Helm chart via Ingress

In order to deploy via ingress, the target cloud will need an ingress controller available in kubernetes, and traffic will need to be routed to that controller properly.  This is currently supported somewhat differently across different clouds, but details can be found below for IBM, Azure, and AWS.


### Deploy via Ingress on IBM Cloud

On IBM Cloud, an ingress controller is automatically installed in the kubernetes cluster and a load balancer is attached to it.  You will need to identify the ingress subdomain.

1. Run `ibmcloud ks cluster get --cluster <<CLUSTER_NAME_OR_ID>>`.
1. Update `ibm-ingress-enabled-values.yaml` and replace `<<INGRESS_SUBDOMAIN>>` with the `Ingress Subdomain` value from the prior step.
1. Deploy the helm chart using the updated yaml: `helm install ingestion . -f ibm-ingress-enabled-values.yaml`.

Once the chart deploys, you will see a list of valid URL's to access the various ingresses available.

### Deploy via Ingress on Azure

On Azure, an ingress controller is automatically installed in the kubernetes cluster without any extra steps. You will need to add a DNS Zone to expose the ingress controller via a domain name.

1. In the Azure portal, create a [DNS Zone](http://portal.azure.com/#create/Microsoft.DnsZone).
1. Once created, the generated name of the DNS Zone (i.e. "1234567890.centralus.aksapp.io") will be used to replace `<<INGRESS_SUBDOMAIN>>` in `azure-ingress-enabled-values.yaml`.
1. Deploy the helm chart using the updated yaml: `helm install ingestion . -f azure-ingress-enabled-values.yaml`

Once the chart deploys, you will see a list of valid URL's to access the various ingresses available.

### Deploy via Ingress on AWS

On AWS, an ingress controller is not available by default. You will need to deploy one in order to deploy this chart.

1. Setup an ingress controller on your kubernetes cluster using [these instructions](https://aws.amazon.com/blogs/opensource/network-load-balancer-nginx-ingress-controller-eks).
1. There should now be an NLB deployed to your cluster. You need to identify the DNS name associated with it using: `aws elbv2 describe-load-balancers`.
1. Copy the `DNSName` and update `<<INGRESS_SUBDOMAIN>>` in `aws-ingress-enabled-values.yaml` with it.
1. Deploy the helm chart using the updated yaml: `helm install ingestion . -f aws-ingress-enabled-values.yaml`.

At this point you have an ingress exposed for each endpoint service.  This can be exposed in AWS using [Route 53](https://console.aws.amazon.com/route53).  

1. Create a new [hosted zone](https://console.aws.amazon.com/route53/v2/hostedzones) for your target DNS Name
1. Select your hosted zone.
1. Create a record redirecting all traffic ending with that DNS Name to the governing load balancer.
    1. Set the record name to "*"
    1. Set the record name to "A"
    1. Enable "Alias"
    1. Choose "Alias to Network Load Balancer"
    1. Set the region to your load balancer region.
    1. Choose your network load balancer from the list.
    1. Click Create records.

Route 53 may take some time to propagate and did not consistently work for us in testing, so you may want a tactical work-around while you wait.

Using [Nip.io](https://nip.io/), you can target your load balancer using it's IP address, but provide the necessary service-routing by prefixing the URI appropriately.

1. Find your Load Balancer IP using your favorite name resolution tool (i.e. NSLookup or Dig)
2. Update `aws-ingress-enabled-values.yaml` with "<<IP>.nip.io" (i.e. "1.2.3.4.nip.io")
3. Deploy/redeploy the helm chart: `helm upgrade ingestion . -f aws-ingress-enabled-values.yaml --install`

Once the chart deploys, you will see a list of valid URL's to access the various ingresses available.