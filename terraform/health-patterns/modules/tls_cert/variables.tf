#
# (C) Copyright IBM Corp. 2021, 2021
#
# SPDX-License-Identifier: Apache-2.0
#
variable "namespace" {
  description = "Kubernetes namespace to deploy to."
  type        = string
}

variable "service_names" {
  description = "List of services names (DNS names) to generate TLS certificates for."
  type        = list(string)
}

variable "alt_service_names" {
  description = "Optional map of additional alternate service names to include in the generated TLS certificate, keyed by the values in `services_names`."
  type        = map(list(string))
  default     = {}
}

variable "organization" {
  description = "Organization name (OU) for TLS certificate"
  type        = string
}

variable "private_key_pem" {
  description = "Private key for generated certificate."
  type        = string
  # sensitive = true
  default = ""
}

variable "algorithm" {
  description = "Public key algorithm for generated key."
  type        = string
  default     = "ECDSA"

  validation {
    condition     = contains(["RSA", "ECDSA"], var.algorithm)
    error_message = "Must be a known algorithm: RSA, ECDSA."
  }
}

variable "ecdsa_curve" {
  description = <<ENDDESC
When `algorithm` is "ECDSA", the name of the elliptic curve to use. May be any one of "P224", "P256", "P384" or "P521", with "P384" as the default.
ENDDESC
  type        = string
  default     = "P384"

  validation {
    condition     = contains(["P224", "P256", "P384", "P521"], var.ecdsa_curve)
    error_message = "Must be any one of \"P224\", \"P256\", \"P384\" or \"P521\"."
  }
}

variable "rsa_bits" {
  description = <<ENDDESC
When `algorithm` is "RSA", the size of the generated RSA key in bits. Defaults to 2048.
ENDDESC
  type        = string
  default     = 2048
}
