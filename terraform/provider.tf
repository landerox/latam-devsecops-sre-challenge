terraform {
  backend "gcs" {
    # El bloque del backend está vacío porque los valores del bucket y el prefijo
    # se pasan dinámicamente con `-backend-config` y se gestionan mediante secretos
    # de GitHub para mayor seguridad.
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
