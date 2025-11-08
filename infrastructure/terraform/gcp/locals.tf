locals {
  environment        = "prod"
  sql_instance_name  = "ibtracs-sql"
  sql_database_name  = "ibtracs"
  sql_user_name      = "ibtracs_app"
  backend_sa_name    = "ibtracs-backend"
  updater_sa_name    = "ibtracs-updater"
  frontend_bucket    = "${var.project_id}-ibtracs-frontend"
  artifact_repo_name = var.artifact_registry_repo
}

