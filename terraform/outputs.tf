output "exchange_rates_dataset_id" {
  value       = module.exchange_rates_dataset.dataset_id
  description = "The ID of the BigQuery dataset for exchange rates"
}

output "currency_exchange_rate_table_id" {
  value       = module.currency_exchange_rate_table.table_id
  description = "The ID of the BigQuery table for currency exchange rates"
}

output "pubsub_topic_name" {
  value       = google_pubsub_topic.currency_exchange_rate_topic.name
  description = "The name of the Pub/Sub topic"
}

output "pubsub_subscription_name" {
  value       = google_pubsub_subscription.currency_exchange_rate_subscription.name
  description = "The name of the Pub/Sub subscription"
}

output "cloud_run_url" {
  value       = google_cloud_run_service.exchange_api.status[0].url
  description = "The URL of the Cloud Run service."
}
