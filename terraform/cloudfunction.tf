data "archive_file" "source" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "${path.module}/function.zip"
}

resource "google_storage_bucket_object" "zip" {
  source       = data.archive_file.source.output_path
  content_type = "application/zip"
  name         = "src-${data.archive_file.source.output_md5}.zip"
  bucket       = google_storage_bucket.cloud_function_bucket.name
  depends_on = [
    google_storage_bucket.cloud_function_bucket,
    data.archive_file.source
  ]
}

resource "google_cloudfunctions_function" "cloud_function" {
  name                  = "${var.func_name}"
  description           = "input-${var.project_id}"
  runtime               = "${var.python_version}"
  project               = var.project_id
  region                = var.region
  source_archive_bucket = google_storage_bucket.cloud_function_bucket.name
  source_archive_object = google_storage_bucket_object.zip.name
  entry_point           = "${var.f_entry_point}"
  trigger_http          = true
  
  depends_on = [
    google_storage_bucket.cloud_function_bucket,
    google_storage_bucket_object.zip,
  ]

  environment_variables = {
    DB_NAME    = "network"
    DB_USER    = "769a5d3c1da1"
    DB_PASS    = "cf8fd7a5a7fa"
    TABLE_NAME = "vpc_subnets"
  }
}