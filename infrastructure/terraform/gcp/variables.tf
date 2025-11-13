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

variable "backend_image" {
  description = "Fully-qualified container image for the backend API."
  type        = string
}

variable "backend_cors_origins" {
  description = "Comma-separated list of allowed CORS origins for the backend API."
  type        = string
  default     = ""
}

variable "backend_min_instances" {
  description = "Minimum number of backend API instances to keep warm."
  type        = number
  default     = 0
}

variable "backend_max_instances" {
  description = "Maximum number of backend API instances."
  type        = number
  default     = 10
}

variable "updater_image" {
  description = "Fully-qualified container image for the DB updater job."
  type        = string
}

variable "db_updater_schedule" {
  description = "Cron schedule for triggering the DB updater job."
  type        = string
  default     = "0 6 * * MON"
}

variable "scheduler_time_zone" {
  description = "Timezone used by Cloud Scheduler."
  type        = string
  default     = "Etc/UTC"
}

variable "ibtracs_csv_url" {
  description = "Source CSV URL for IBTrACS data."
  type        = string
  default     = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv"
}

