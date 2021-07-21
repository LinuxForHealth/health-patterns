# Ingress Subdomain Setup

In order to deploy via ingress, the target cloud will need an ingress controller available in kubernetes, and traffic will need to be routed to that controller properly.  This is currently supported somewhat differently across different clouds, but details can be found below for IBM, Azure, and AWS.


### Ingress on IBM Cloud

On IBM Cloud, an ingress controller is automatically installed in the kubernetes cluster and a load balancer is attached to it.  In order to identify the ingress subdomain simply run:

1. `ibmcloud ks cluster get --cluster <<CLUSTER_NAME_OR_ID>>`.

This will return to you a list of information including the ingress subdomain for your cluster.

### Ingress on Azure

On Azure, an ingress controller is automatically installed in the kubernetes cluster without any extra steps. You will need to add a DNS Zone to expose the ingress controller via a domain name.

1. In the Azure portal, create a [DNS Zone](http://portal.azure.com/#create/Microsoft.DnsZone).
1. Once created, the generated name of the DNS Zone (i.e. "1234567890.centralus.aksapp.io") will be used as your ingress subdomain in the Clinical Ingestion helm chart.

### Ingress on AWS

On AWS, an ingress controller is not available by default. You will need to deploy one in order to deploy this chart.

1. Setup an ingress controller on your kubernetes cluster using [these instructions](https://aws.amazon.com/blogs/opensource/network-load-balancer-nginx-ingress-controller-eks).
1. There should now be an NLB deployed to your cluster. You need to identify the DNS name associated with it using: `aws elbv2 describe-load-balancers`.
1. The generated `DNSName` will be used as your ingress subdomain in the Clinical Ingestion Helm chart.

After you have completed deployment of the Clinical Ingestion Helm chart you will have an ingress exposed for each endpoint service.  However, this is not reachable yet in AWS.  It can be exposed externally using [Route 53](https://console.aws.amazon.com/route53).  

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

##Quick deploy for AWS:##

If configuring Route 53 is too daunting in AWS, another option that can get you up and running quickly is to use [Nip.io](https://nip.io/).  This service will automatically route traffic to the corresponding IP address, using a formatted prefix on the hostname:

1. Find your Load Balancer IP using your favorite name resolution tool (i.e. NSLookup or Dig)
2. For the ingress subdomain, use this format: "<<IP>.nip.io" (i.e. "1.2.3.4.nip.io")

This will result in automatically routing traffic to the back-end ingress controller, which will, in turn, pass the data onto individual services.
