provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

variable namespace {
  description = "Target deploy namespace"
  type        = string
  default     = "alvearie"
}

variable hostname {
  description = "Hostname to use for ingress access of services"
  type        = string
}

resource "helm_release" "ascvd-from-fhir" {
  name       = "ascvd-from-fhir"
  repository = "https://alvearie.github.io/health-analytics/charts"
  chart      = "ascvd-from-fhir"
  namespace  = var.namespace

  set {
    name  = "ingress.enabled"
    value = "true"
  }

  set {
    name  = "ingress.hostname"
    value = "${var.hostname}"
  }
}