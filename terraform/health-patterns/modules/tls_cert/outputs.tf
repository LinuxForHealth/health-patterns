#
# (C) Copyright IBM Corp. 2021, 2021
#
# SPDX-License-Identifier: Apache-2.0
#
output "certificates" {
  description = "The public certificates for each service."
  value       = { for key, value in kubernetes_certificate_signing_request.csr : (key) => value.certificate }
}
