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
  default     = "my-postgres"
}