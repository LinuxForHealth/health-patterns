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

resource "helm_release" "ascvd" {
  name        = "ascvd"
  repository  = "https://alvearie.github.io/health-analytics/charts"
  chart       = "ascvd"
  namespace   = var.namespace
}