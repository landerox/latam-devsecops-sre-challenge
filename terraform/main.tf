module "exchange_rates_dataset" {
  source      = "./modules/bigquery_dataset"
  dataset_id  = "exchange_rates"
  project_id  = var.project_id
  location    = var.location
  description = "Dataset to store exchange rates"
}

module "currency_exchange_rate_table" {
  source              = "./modules/bigquery_table"
  dataset_id          = module.exchange_rates_dataset.dataset_id
  table_name          = "currency_exchange_rate"
  project_id          = var.project_id
  schema_file         = "${path.module}/bigquery_schemas/currency_exchange_rate_schema.json"
  description         = "Table to stora currency exchange rates"
  deletion_protection = false
  enable_partitioning = true
  partition_type      = "DAY"
  partition_field     = "load_ts"

  depends_on = [
    module.exchange_rates_dataset
  ]
}

resource "google_pubsub_topic" "currency_exchange_rate_topic" {
  name    = var.pubsub_topic_name
  project = var.project_id
}

resource "google_pubsub_subscription" "currency_exchange_rate_subscription" {
  name                 = var.pubsub_subscription_name
  topic                = google_pubsub_topic.currency_exchange_rate_topic.name
  ack_deadline_seconds = 20
}

resource "google_cloud_run_service" "exchange_api" {
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      service_account_name = var.service_account_email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository}/${var.cloud_run_service_name}:${var.tag}"

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
          requests = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }

        ports {
          container_port = 8080
        }
      }
    }
  }

  traffic {
    latest_revision = true
    percent         = 100
  }
}

# Permitir acceso público al servicio de Cloud Run
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.exchange_api.location
  project  = google_cloud_run_service.exchange_api.project
  service  = google_cloud_run_service.exchange_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
