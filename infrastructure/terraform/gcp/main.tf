resource "google_project_service" "required" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "compute.googleapis.com",
    "dns.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com"
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

resource "random_password" "db_root" {
  length  = 24
  special = true
}

resource "random_password" "db_app" {
  length           = 24
  special          = true
  override_special = "-_@"
}

resource "google_sql_database_instance" "postgres" {
  name             = local.sql_instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_instance_tier
    disk_size         = var.db_disk_size_gb
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    availability_type = "ZONAL"

    backup_configuration {
      enabled = false
    }

    ip_configuration {
      ipv4_enabled = true

      authorized_networks {
        name  = "public"
        value = "0.0.0.0/0"
      }
    }
  }

  root_password       = random_password.db_root.result
  deletion_protection = false

  depends_on = [google_project_service.required]
}

resource "google_sql_database" "ibtracs" {
  name     = local.sql_database_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app" {
  name     = local.sql_user_name
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_app.result
}

resource "google_artifact_registry_repository" "containers" {
  provider      = google-beta
  location      = var.region
  repository_id = local.artifact_repo_name
  description   = "Container images for IBTrACS mapper services"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }

  depends_on = [google_project_service.required]
}

resource "google_service_account" "backend" {
  account_id   = local.backend_sa_name
  display_name = "IBTrACS Backend API"
}

resource "google_service_account" "updater" {
  account_id   = local.updater_sa_name
  display_name = "IBTrACS DB Updater"
}

resource "google_project_iam_member" "backend_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "updater_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.updater.email}"
}

resource "google_storage_bucket" "frontend" {
  name                        = local.frontend_bucket
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}
# GCP infrastructure configuration
# This module sets up GCP resources for hosting the application

# TODO: Configure GCP resources
# - Cloud Run for API
# - Cloud Storage for frontend
# - Cloud Scheduler for db-updater
# - IAM roles and permissions

