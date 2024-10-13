output "dataset_id" {
  value       = google_bigquery_dataset.dataset.dataset_id
  description = "The ID of the BigQuery dataset"
}

output "self_link" {
  value       = google_bigquery_dataset.dataset.self_link
  description = "The self-link of the BigQuery dataset"
}

output "creation_time" {
  value       = google_bigquery_dataset.dataset.creation_time
  description = "The creation time of the BigQuery dataset"
}
