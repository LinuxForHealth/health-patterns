######################
##      ASCVD       ##
######################
module "ascvd" {
  source           = "./modules/ascvd"
  namespace        = var.namespace
}

######################
## ASCVD  From FHIR ##
######################
module "ascvd-from-fhir" {
  source          = "./modules/ascvd-from-fhir"
  namespace       = var.namespace
  hostname        = var.hostname
}

##############################
## TLS Certificate / Secret ##
##############################
module "tls_cert" {
  source          = "./modules/tls_cert"
  namespace       = var.namespace
  service_names   = ["${var.namespace}"]
  organization    = var.tls_cert_organization
}

######################
##     PostGres     ##
######################
module "postgres" {
  source          = "./modules/postgres"
  name            = var.postgres_name
  namespace       = var.namespace
}

######################
##       FHIR       ##
######################
module "fhir" {
  source          = "./modules/fhir"
  namespace       = var.namespace
  tls_secret_name = "${var.namespace}-tls"
  hostname        = var.hostname
  postgres_name   = var.postgres_name
  depends_on      = [module.postgres]
}