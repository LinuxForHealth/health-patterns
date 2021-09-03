variable namespace {
  description = "Target deploy namespace"
  type        = string
}

variable hostname {
  description = "Hostname to use for ingress access of services"
  type        = string
}

variable "tls_cert_organization" {
  description = "Organization name (OU) for TLS certificate"
  type        = string
}

variable "postgres_name" {
  description = "PostGres server name"
  type        = string
  default     = "fhir-postgres"
}

variable "deid_postgres_name" {
  description = "Deid-PostGres server name"
  type        = string
  default     = "fhir-deid-postgres"
}

variable ingressClass {
  description = ""
  type        = string
  default     = "public-iks-k8s-nginx"
}

variable valueFile {
  description = "The name of the value.yaml to use while deploying the Health Patterns helm chart"
  type = string
  default = "clinical_ingestion.yaml"
}
