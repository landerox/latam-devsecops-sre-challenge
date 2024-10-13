# Especifica la versión mínima de Terraform y el proveedor de Google requerido.
terraform {
  required_version = ">= 1.9.7"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.6.0"
    }
  }
}
