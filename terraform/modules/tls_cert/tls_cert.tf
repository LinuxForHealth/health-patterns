#
# (C) Copyright IBM Corp. 2021, 2021
#
# SPDX-License-Identifier: Apache-2.0
#

/**
 * Terraform module to generate a Kubernetes secret with a signed TLS certificate.
 */

# key used to generate Certificate Request
resource "tls_private_key" "private_key" {
  count       = local.generate_private_key ? 1 : 0
  algorithm   = var.algorithm
  ecdsa_curve = var.ecdsa_curve
  rsa_bits    = var.rsa_bits
}

locals {
  dns_names            = concat([for service in var.service_names : [service, "${service}.${var.namespace}", "${service}.${var.namespace}.svc"]]...)
  generate_private_key = (var.private_key_pem == "")
}

locals {
  // expand the alternate names
  alt_dns_names = {
    for svc_name, alt_names in var.alt_service_names : svc_name => flatten(
      [for alt_name in alt_names : [alt_name, "${alt_name}.${var.namespace}", "${alt_name}.${var.namespace}.svc"]]
    )
  }
}

# Construct the CSR
resource "tls_cert_request" "cert_request" {
  for_each = toset(var.service_names)

  key_algorithm   = var.algorithm
  private_key_pem = local.generate_private_key ? tls_private_key.private_key[0].private_key_pem : var.private_key_pem
  dns_names = flatten([
    [each.key, "${each.key}.${var.namespace}", "${each.key}.${var.namespace}.svc"],
    lookup(local.alt_dns_names, each.key, [])
  ])

  subject {
    common_name  = each.key
    organization = var.organization
  }
}

# Issue the certificate signing request
resource "kubernetes_certificate_signing_request" "csr" {
  for_each = toset(var.service_names)

  metadata {
    generate_name = "${each.key}-csr"
  }

  spec {
    usages  = ["client auth", "server auth"]
    request = tls_cert_request.cert_request[each.key].cert_request_pem
  }
  auto_approve = true
}

data "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }
}

# Get the signed certificate from the request and save it in the secret
resource "kubernetes_secret" "secret" {
  for_each = toset(var.service_names)

  metadata {
    name      = "${each.key}-tls"
    namespace = data.kubernetes_namespace.namespace.metadata[0].name
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
  data = {
    "tls.crt" = kubernetes_certificate_signing_request.csr[each.key].certificate
    "tls.key" = local.generate_private_key ? tls_private_key.private_key[0].private_key_pem : var.private_key_pem
  }
  type = "kubernetes.io/tls"
}
