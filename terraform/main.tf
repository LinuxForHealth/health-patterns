module "ascvd" {
  source                    = "./modules/ascvd"
  namespace                 = var.namespace
}

module "ascvd-from-fhir" {
  source                    = "./modules/ascvd-from-fhir"
  namespace                 = var.namespace
  hostname                  = "${var.namespace}.${var.hostname}"
}

module "tls_cert" {
  source                    = "./modules/tls_cert"
  namespace                 = var.namespace
  service_names             = ["${var.namespace}"]
  organization              = var.tls_cert_organization
}

module "postgres" {
  source                    = "./modules/postgres"
  name                      = "my-postgres"
  namespace                 = var.namespace
}

module "fhir" {
  source                    = "./modules/fhir"
  namespace                 = var.namespace
  tls_secret_name           = "${var.namespace}-tls"
  hostname                  = "${var.namespace}.${var.hostname}"
  postgres_name             = "my-postgres"
}
