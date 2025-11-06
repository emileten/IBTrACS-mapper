# Main Terraform configuration
# This file orchestrates all infrastructure components

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Include Supabase resources
module "supabase" {
  source = "./supabase"
}

# Include GCP resources
module "gcp" {
  source = "./gcp"
}

