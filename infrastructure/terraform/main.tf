terraform {
  required_version = ">= 1.6.0"
}

module "gcp" {
  source = "./gcp"

  project_id             = var.project_id
  region                 = var.region
  zone                   = var.zone
  root_domain            = var.root_domain
  api_subdomain          = var.api_subdomain
  frontend_subdomain     = var.frontend_subdomain
  db_instance_tier       = var.db_instance_tier
  db_disk_size_gb        = var.db_disk_size_gb
  artifact_registry_repo = var.artifact_registry_repo
  backend_image          = var.backend_image
  updater_image          = var.updater_image
  backend_cors_origins   = var.backend_cors_origins
}

