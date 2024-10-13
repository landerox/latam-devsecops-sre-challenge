variable "project_id" {
  description = "The project ID in Google Cloud. This value is set via GitHub Secrets."
  type        = string
}

variable "location" {
  description = "The location in Google Cloud for BigQuery. This value is set via GitHub Secrets."
  type        = string
}

variable "region" {
  description = "The region in Google Cloud for other services. This value is set via GitHub Secrets."
  type        = string
}

variable "bucket_name" {
  description = "The name of the GCS bucket to store Terraform state. This value is set via GitHub Secrets."
  type        = string
}

variable "terraform_state" {
  description = "The prefix to store the Terraform state file. This value is set via GitHub Secrets."
  type        = string
}

variable "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic"
  type        = string
}

variable "pubsub_subscription_name" {
  description = "The name of the Pub/Sub subscription"
  type        = string
}

variable "cloud_run_service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "exchange-api"
}

variable "image_name" {
  description = "The name of the Docker image to be deployed in Cloud Run."
  type        = string
  default     = "latest"
}

variable "tag" {
  description = "The tag of the Docker image to be deployed in Cloud Run."
  type        = string
  default     = "latest"
}

variable "repository" {
  description = "The name of the Artifact Registry repository"
  type        = string
}

variable "service_account_email" {
  description = "The service account to run the Cloud Run service"
  type        = string
}
