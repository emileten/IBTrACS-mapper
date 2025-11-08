variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Primary region for resources"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "Default zone"
  type        = string
  default     = "europe-west1-b"
}

variable "root_domain" {
  description = "Root domain that will host the frontend and API"
  type        = string
}

variable "api_subdomain" {
  description = "Subdomain for the API service"
  type        = string
  default     = "api"
}

variable "frontend_subdomain" {
  description = "Subdomain for the frontend (use @ for root)"
  type        = string
  default     = "@"
}

variable "db_instance_tier" {
  description = "Machine tier for Cloud SQL instance"
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size_gb" {
  description = "Disk size for Cloud SQL instance"
  type        = number
  default     = 20
}

variable "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "ibtracs-mapper"
}

