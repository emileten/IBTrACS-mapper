locals {
  environment          = "prod"
  sql_instance_name    = "ibtracs-sql"
  sql_database_name    = "ibtracs"
  sql_user_name        = "ibtracs_app"
  backend_sa_name      = "ibtracs-backend"
  updater_sa_name      = "ibtracs-updater"
  scheduler_sa_name    = "ibtracs-scheduler"
  backend_service_name = "ibtracs-backend-api"
  updater_job_name     = "ibtracs-db-updater"
  frontend_bucket      = "${var.project_id}-ibtracs-frontend"
  artifact_repo_name   = var.artifact_registry_repo
  dns_zone_name        = "ibtracs-mapper-zone"

  frontend_fqdn = var.frontend_subdomain == "@" ? var.root_domain : "${var.frontend_subdomain}.${var.root_domain}"
  api_fqdn      = var.api_subdomain == "@" ? var.root_domain : "${var.api_subdomain}.${var.root_domain}"

  backend_image = var.backend_image
  updater_image = var.updater_image
}

