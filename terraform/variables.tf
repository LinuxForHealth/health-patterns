variable namespace {
 type = string
 default = "alvearie"
}

variable hostname {
 type = string
 default = "wh-health-patterns.dev.watson-health.ibm.com"
}

variable "tls_cert_organization" {
  description = "Organization name (OU) for TLS certificate"
  type        = string
  default     = "IBM"
}
