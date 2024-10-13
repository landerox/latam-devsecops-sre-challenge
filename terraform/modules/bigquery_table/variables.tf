variable "dataset_id" {
  description = "The ID of the dataset in BigQuery"
  type        = string
}

variable "table_name" {
  description = "The name of the BigQuery table"
  type        = string
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "schema_file" {
  description = "The path to the schema file for the BigQuery table"
  type        = string
}

variable "description" {
  description = "Description of the BigQuery table"
  type        = string
}

variable "deletion_protection" {
  description = "Enable or disable deletion protection for the BigQuery table"
  type        = bool
  default     = false
}

variable "enable_partitioning" {
  description = "Whether to enable time-based partitioning"
  type        = bool
}

variable "partition_type" {
  description = "The type of time partitioning"
  type        = string
  default     = "DAY"
}

variable "partition_field" {
  description = "The field to use for partitioning"
  type        = string
}
