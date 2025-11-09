output "database_instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_name" {
  description = "Primary application database name"
  value       = google_sql_database.ibtracs.name
}

output "database_user" {
  description = "Application database user"
  value       = google_sql_user.app.name
}

output "database_password" {
  description = "Password for the application database user"
  value       = google_sql_user.app.password
  sensitive   = true
}

output "database_url" {
  description = "Connection URL for the application database"
  value       = local.database_url
  sensitive   = true
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository"
  value       = google_artifact_registry_repository.containers.repository_id
}

output "frontend_bucket" {
  description = "GCS bucket for hosting the frontend build"
  value       = google_storage_bucket.frontend.name
}

output "backend_service_account" {
  description = "Service account email for the backend API"
  value       = google_service_account.backend.email
}

output "updater_service_account" {
  description = "Service account email for the updater job"
  value       = google_service_account.updater.email
}

output "scheduler_service_account" {
  description = "Service account email used by Cloud Scheduler"
  value       = google_service_account.scheduler.email
}

output "backend_service_url" {
  description = "Default Cloud Run URL for the backend API"
  value       = google_cloud_run_v2_service.backend.uri
}

output "load_balancer_ip" {
  description = "Global static IP address serving the HTTPS load balancer"
  value       = google_compute_global_address.frontend.address
}

output "frontend_domain" {
  description = "Frontend custom domain"
  value       = local.frontend_fqdn
}

output "api_domain" {
  description = "API custom domain"
  value       = local.api_fqdn
}

