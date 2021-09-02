variable namespace {
  description = "Target deploy namespace"
  type        = string
  default     = "alvearie"
}

variable hostname {
  description = "Hostname to use for ingress access of services"
  type        = string
}

variable tls_secret_name {
  description = "Name of secret used to store TLS certificate"
  type        = string
}

variable postgres_name {
  description = "PostGres server name"
  type        = string
}

variable name {
  description = "Name of FHIR server"
  type        = string
  default     = "fhir"
}

resource "helm_release" "fhir" {
  name        = var.name
  repository  = "https://alvearie.io/alvearie-helm"
  chart       = "ibm-fhir-server"
  namespace   = var.namespace

  values      = [
    "${file("${path.module}/values.yaml")}"
  ]

  set {
    name      = "ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "ingress.tls[0].secretName"
    value     = var.tls_secret_name
  }

  set {
    name      = "db.host"
    value     = var.postgres_name
  }

  set {
    name      = "db.passwordSecret"
    value     = var.postgres_name
  }

  set {
    name      = "db.dbSecret"
    value     = var.postgres_name
  }

  set {
    name      = "ingress.rules[0].host"
    value     = var.hostname
  }

  set {
    name      = "ingress.rules[0].paths[0]"
    value     = format("/%s(/|$)(.*)", var.name)
  }
}