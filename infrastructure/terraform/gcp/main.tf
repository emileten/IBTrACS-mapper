resource "google_project_service" "required" {
  for_each = toset([
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
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

data "google_project" "current" {
  project_id = var.project_id
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

locals {
  database_url      = "postgresql://${google_sql_user.app.name}:${random_password.db_app.result}@${google_sql_database_instance.postgres.ip_address[0].ip_address}:5432/${google_sql_database.ibtracs.name}"
  frontend_dns_name = "${local.frontend_fqdn}."
  api_dns_name      = "${local.api_fqdn}."
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

resource "google_service_account" "scheduler" {
  account_id   = local.scheduler_sa_name
  display_name = "IBTrACS Scheduler"
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

resource "google_service_account_iam_member" "scheduler_token_creator" {
  service_account_id = google_service_account.scheduler.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
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

resource "google_storage_bucket_iam_member" "frontend_public" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_cloud_run_v2_service" "backend" {
  provider = google-beta
  name     = local.backend_service_name
  location = var.region

  template {
    service_account = google_service_account.backend.email

    scaling {
      min_instance_count = var.backend_min_instances
      max_instance_count = var.backend_max_instances
    }

    containers {
      image = local.backend_image

      ports {
        container_port = 8000
      }

      env {
        name  = "DATABASE_URL"
        value = local.database_url
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_sql_database_instance.postgres
  ]
}

resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  provider = google-beta
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_job" "db_updater" {
  provider = google-beta
  name     = local.updater_job_name
  location = var.region

  template {
    task_count = 1
    template {
      service_account = google_service_account.updater.email
      max_retries     = 1

      containers {
        image = local.updater_image

        env {
          name  = "DATABASE_URL"
          value = local.database_url
        }

        env {
          name  = "IBTRACS_CSV_URL"
          value = var.ibtracs_csv_url
        }

        resources {
          limits = {
            "memory" = "2Gi"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_sql_database_instance.postgres
  ]
}

resource "google_cloud_run_v2_job_iam_member" "db_updater_invoker" {
  provider = google-beta
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.db_updater.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

resource "google_compute_backend_bucket" "frontend" {
  name        = "ibtracs-frontend-backend"
  bucket_name = google_storage_bucket.frontend.name
  enable_cdn  = true
}

resource "google_compute_region_network_endpoint_group" "api" {
  name                  = "ibtracs-api-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = google_cloud_run_v2_service.backend.name
  }
}

resource "google_compute_backend_service" "api" {
  name                  = "ibtracs-api-backend"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTPS"
  timeout_sec           = 30

  backend {
    group = google_compute_region_network_endpoint_group.api.id
  }
}

resource "google_compute_url_map" "main" {
  name = "ibtracs-url-map"

  default_service = google_compute_backend_bucket.frontend.self_link

  host_rule {
    hosts        = [local.api_fqdn]
    path_matcher = "api-matcher"
  }

  path_matcher {
    name            = "api-matcher"
    default_service = google_compute_backend_service.api.self_link
  }
}

resource "google_compute_managed_ssl_certificate" "primary" {
  name = "ibtracs-managed-cert"

  managed {
    domains = distinct([local.frontend_fqdn, local.api_fqdn])
  }
}

resource "google_compute_target_https_proxy" "primary" {
  name    = "ibtracs-https-proxy"
  url_map = google_compute_url_map.main.self_link
  ssl_certificates = [
    google_compute_managed_ssl_certificate.primary.id
  ]
}

resource "google_compute_global_address" "frontend" {
  name = "ibtracs-frontend-ip"
}

resource "google_compute_global_forwarding_rule" "https" {
  name                  = "ibtracs-https-forwarding"
  load_balancing_scheme = "EXTERNAL"
  target                = google_compute_target_https_proxy.primary.self_link
  port_range            = "443"
  ip_protocol           = "TCP"
  ip_address            = google_compute_global_address.frontend.address
}

resource "google_cloud_scheduler_job" "db_updater" {
  name        = "ibtracs-db-updater-weekly"
  description = "Weekly refresh of IBTrACS data"
  region      = var.region
  schedule    = var.db_updater_schedule
  time_zone   = var.scheduler_time_zone

  http_target {
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.db_updater.name}:run"
    http_method = "POST"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      name = "projects/${var.project_id}/locations/${var.region}/jobs/${google_cloud_run_v2_job.db_updater.name}"
    }))

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = "https://${var.region}-run.googleapis.com/"
    }
  }

  retry_config {
    retry_count = 0
  }

  depends_on = [
    google_cloud_run_v2_job.db_updater,
    google_service_account_iam_member.scheduler_token_creator
  ]
}

resource "google_dns_managed_zone" "primary" {
  name        = local.dns_zone_name
  dns_name    = "${var.root_domain}."
  description = "Managed zone for IBTrACS Mapper"
}

resource "google_dns_record_set" "frontend_a" {
  name         = local.frontend_dns_name
  managed_zone = google_dns_managed_zone.primary.name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.frontend.address]

  depends_on = [google_compute_global_address.frontend]
}

resource "google_dns_record_set" "api_a" {
  name         = local.api_dns_name
  managed_zone = google_dns_managed_zone.primary.name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.frontend.address]

  depends_on = [google_compute_global_address.frontend]
}
