provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

variable namespace {
 type = string
 default = "alvearie"
}

variable name {
 type = string
 default = "postgres"
}

resource "helm_release" "postgres" {
  name       = var.name
  chart      = "bitnami/postgresql"
  namespace = var.namespace

  set {
    name = "fullnameOverride"
    value = var.name
  }
 
  set {
    name = "postgresqlExtendedConf.maxPreparedTransactions"
    value = 100
  }
}