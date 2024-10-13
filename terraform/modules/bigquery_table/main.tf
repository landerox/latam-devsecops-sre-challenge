resource "google_bigquery_table" "table" {
  dataset_id          = var.dataset_id
  table_id            = var.table_name
  project             = var.project_id
  schema              = file(var.schema_file)
  description         = var.description
  deletion_protection = var.deletion_protection

  dynamic "time_partitioning" {
    for_each = var.enable_partitioning ? [1] : []
    content {
      type  = var.partition_type
      field = var.partition_field
    }
  }
}
