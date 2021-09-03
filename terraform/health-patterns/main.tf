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
module "fhir-postgres" {
  source          = "./modules/postgres"
  name            = var.postgres_name
  namespace       = var.namespace
}

######################
##  Deid PostGres   ##
######################
module "fhir-deid-postgres" {
  source          = "./modules/postgres"
  name            = var.deid_postgres_name
  namespace       = var.namespace
}

resource "helm_release" "health-patterns" {
  name =      "ingestion"
  chart       = "../../helm-charts/health-patterns"
  namespace   = var.namespace
  depends_on      = [module.fhir-postgres, module.fhir-deid-postgres]

  values      = [
    "${file("../../helm-charts/health-patterns/${var.valueFile}")}"
  ]

  set {
    name      = "ingress.class"
    value     = var.ingressClass
  }

  set {
    name      = "ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "ascvd-from-fhir.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "hl7-resource-generator.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "nlp-insights.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "nifi-registry.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "nifi.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "deid.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "deid-prep.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "term-services-prep.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "expose-kafka.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "cql-bulkexport.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "cohort-service.ingress.hostname"
    value     = var.hostname
  }







  set {
    name      = "fhir.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "fhir.ingress.tls[0].secretName"
    value     = "${var.namespace}-tls"
  }

  set {
    name      = "fhir.db.host"
    value     = var.postgres_name
  }

  set {
    name      = "fhir.db.passwordSecret"
    value     = var.postgres_name
  }

  set {
    name      = "fhir.db.dbSecret"
    value     = var.postgres_name
  }

  set {
    name      = "fhir.ingress.rules[0].host"
    value     = var.hostname
  }

  set {
    name      = "fhir.ingress.rules[0].paths[0]"
    value     = "/fhir(/|$)(.*)"
  }



  set {
    name      = "fhir-deid.ingress.hostname"
    value     = var.hostname
  }

  set {
    name      = "fhir-deid.ingress.tls[0].secretName"
    value     = "${var.namespace}-tls"
  }

  set {
    name      = "fhir-deid.db.host"
    value     = var.deid_postgres_name
  }

  set {
    name      = "fhir-deid.db.passwordSecret"
    value     = var.deid_postgres_name
  }

  set {
    name      = "fhir-deid.db.dbSecret"
    value     = var.deid_postgres_name
  }

  set {
    name      = "fhir-deid.ingress.rules[0].host"
    value     = var.hostname
  }

  set {
    name      = "fhir-deid.ingress.rules[0].paths[0]"
    value     =  "/fhir-deid(/|$)(.*)"
  }
}