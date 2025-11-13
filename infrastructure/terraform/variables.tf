variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Primary region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "Primary zone"
  type        = string
  default     = "europe-west1-b"
}

variable "root_domain" {
  description = "Root domain name"
  type        = string
}

variable "api_subdomain" {
  description = "API subdomain"
  type        = string
  default     = "api"
}

variable "frontend_subdomain" {
  description = "Frontend subdomain (use @ for root)"
  type        = string
  default     = "@"
}

variable "db_instance_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size_gb" {
  description = "Cloud SQL disk size"
  type        = number
  default     = 20
}

variable "artifact_registry_repo" {
  description = "Artifact Registry repository ID"
  type        = string
  default     = "ibtracs-mapper"
}

variable "backend_image" {
  description = "Fully qualified container image for the backend API."
  type        = string
}

variable "updater_image" {
  description = "Fully qualified container image for the DB updater job."
  type        = string
}

variable "backend_cors_origins" {
  description = "Comma-separated list of allowed CORS origins for the backend API."
  type        = string
  default     = ""
}

