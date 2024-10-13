output "table_id" {
  value       = google_bigquery_table.table.table_id
  description = "The BigQuery Table ID"
}

output "table_self_link" {
  value       = google_bigquery_table.table.self_link
  description = "The self-link of the BigQuery table"
}

output "table_creation_time" {
  value       = google_bigquery_table.table.creation_time
  description = "The creation time of the BigQuery table"
}
