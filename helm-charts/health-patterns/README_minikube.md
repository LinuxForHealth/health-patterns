# Health Patterns Helm Chart on minikube

In order to deploy Health Patterns to minikube, follow these simple setup steps:

* Install [minikube](https://minikube.sigs.k8s.io/docs/start/).

* Deploy minikube with at least 10G (may require more) of memory:

`minikube start --memory='max' --cpus='max'`

* Enable ingress: 

`minikube addons enable ingress`

The kubernetes dashboard is accessible using:

`minikube dashboard`

* Update ingress values in helm-charts/health-patterns/values.yaml: 

```
ingress:
  enabled: &ingressEnabled true
  class: &ingressClass nginx
  hostname: &hostname localhost
```

* Install the helm chart. Follow the instructions [here](https://github.com/Alvearie/health-patterns/blob/main/helm-charts/health-patterns/README_Helm.md#deploy).

* Once installed, run:

`minikube tunnel`

This will allow access to services in your cluster.  It will ask for your password and then hang. You can Ctrl+z and `bg` at this point to continue using your terminal.

* Enable port forwarding to the ingress controller:
 
`kubectl port-forward --namespace=ingress-nginx service/ingress-nginx-controller 8080:80 &`


With this, you can now access the services such as:

```
http://localhost:8080/nifi
http://localhost:8080/fhir
http://localhost:8080/expose-kafka
http://localhost:8080/nifi-registry
```