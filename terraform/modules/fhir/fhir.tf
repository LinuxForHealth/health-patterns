provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

variable namespace {
 type = string
 default = "alvearie"
}

variable hostname {
 type = string
 default = "atc.wh-health-patterns.dev.watson-health.ibm.com"
}

variable tls_secret_name {
 type = string
}

variable postgres_name {
 type = string
}

resource "helm_release" "fhir" {
  name       = "fhir"

#  repository = "https://alvearie.github.io/health-patterns/charts"
#  chart      = "fhir"
  chart      = "./ibm-fhir-server"
  namespace = var.namespace

  values = [
    "${file("./ibm-fhir-server/values-nginx.yaml")}"
  ]
  
  set {
    name  = "ingress.hostname"
    value = var.hostname
  }

  set {
    name  = "ingress.tls[0].secretName"
    value = var.tls_secret_name
  }
  
  set {
    name  = "db.host"
    value = var.postgres_name
  }
  set {
    name  = "db.passwordSecret"
    value = var.postgres_name
  }
  set {
    name  = "ingress.hostname"
    value = "${var.namespace}.wh-health-patterns.dev.watson-health.ibm.com"
  }

  set {
    name  = "ingress.tls[0].secretName"
    value = "${var.namespace}-tls" 
  }

  set {
    name  = "ingress.rules[0].host"
    value = "${var.namespace}.wh-health-patterns.dev.watson-health.ibm.com"
  }

  set {
    name  = "ingress.rules[0].paths[0]"
    value = "/"
  }
}