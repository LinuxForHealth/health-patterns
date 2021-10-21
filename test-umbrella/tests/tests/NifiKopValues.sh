#!/bin/bash

# Prepare the values.yaml file for a deployment using NifiKop

# Get to the deployment directory
cd /workspace/$TEST_NAMESPACE/health-patterns/helm-charts/health-patterns

# oidic users
sed -i -e "s/identity: \"replace-me@company.com\"/identity: \"roger.guderian@ibm.com\"/g" values.yaml
sed -i -e "s/name: \"replace.me.no.spaces.or.caps\"/name: \"roger.guderian\"\n    - identity: \"atclark@us.ibm.com\"\n      name: \"adam.t.clark\"/g" values.yaml

# oidc discovery URL
sed -i -e "s/\&oidc_discovery_url \"replace-me\"/\&oidc_discovery_url \"https:\/\/us-east.appid.cloud.ibm.com\/oauth\/v4\/82343deb-31d3-4a15-9c30-469d12651b89\/.well-known\/openid-configuration\"/g" values.yaml

#oidc client and secret
sed -i -e "s/\&oidc_client_id replace-me/\&oidc_client_id 38c44769-91c3-4650-a8d5-b24f8992a821/g" values.yaml
sed -i -e "s/\&oidc_client_secret replace-me/\&oidc_client_secret MmJjODZiNDUtNzdmYS00ZmJlLWFhNDYtZGFmMWFhMmI1MTI2/g" values.yaml

# Enable NifiKop Deployment
sed -i -e "s/\&nifikopDisabled true/\&nifikopDisabled false/g" values.yaml
sed -i -e "s/\&nifikopEnabled false/\&nifikopEnabled true/g" values.yaml

# Deploy NifiKop
echo "Deploy NifiKop"
helm3 repo add orange-incubator https://orange-kubernetes-charts-incubator.storage.googleapis.com/
helm3 repo update
helm3 install nifikop orange-incubator/nifikop --namespace=$TEST_NAMESPACE --version 0.6.3 --set image.tag=v0.6.3-release --set resources.requests.memory=256Mi --set resources.requests.cpu=250m --set resources.limits.memory=256Mi --set resources.limits.cpu=250m --set namespaces={"$TEST_NAMESPACE"}  --wait --timeout 4m0s
