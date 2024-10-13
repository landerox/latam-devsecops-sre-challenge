variable "dataset_id" {
  description = "The ID of the dataset in BigQuery"
  type        = string
}

variable "project_id" {
  description = "The project ID in Google Cloud"
  type        = string
}

variable "location" {
  description = "The location of the dataset"
  type        = string
  default     = "US"
}

variable "description" {
  description = "Description of the dataset"
  type        = string
  default     = "A BigQuery dataset"
}
