# Terraform – Google Cloud deployment

This configuration deploys the full IBTrACS Mapper stack on Google Cloud.

## Provisioned resources

- Required Google Cloud APIs (Run, Cloud SQL, Artifact Registry, Scheduler, Compute, DNS, IAM, Secret Manager)
- Cloud SQL PostgreSQL instance, database, and application user (public IP for now)
- Artifact Registry repository for container images
- Service accounts for backend API, DB updater task, and scheduler trigger
- Cloud Run (v2) service for the FastAPI backend
- Cloud Run (v2) job for the IBTrACS DB updater
- Cloud Scheduler job (weekly, configurable cron) that triggers the updater job with OIDC auth
- GCS bucket for the frontend artefacts + CDN-enabled HTTPS external load balancer
- Serverless network endpoint group + load balancer routing for the API subdomain
- Managed SSL certificate, global forwarding rule, and DNS zone/records for both frontend and API domains

## Usage

1. Ensure you have a Google Cloud project and the Terraform IAM credentials with sufficient permissions (project owner/editor is easiest for development).
2. Populate a `terraform.tfvars` file (or pass variables via CLI):

   ```hcl
   project_id        = "your-project-id"
   region            = "europe-west1"
   zone              = "europe-west1-b"
   root_domain       = "ibtracs-mapper.com"
   ```

3. (Optional) Override image tags or schedules, e.g.:

   ```hcl
   backend_image_name = "backend-api:main"
   updater_image_name = "db-updater:main"
   db_updater_schedule = "0 3 * * *" # every day at 03:00 UTC
   ```

4. Initialise and apply:

   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Next steps

- Restrict Cloud SQL access (Cloud SQL Auth Proxy or private IP)
- Store secrets (DB credentials) in Secret Manager instead of Terraform state
- Harden Cloud Run ingress (allow only load-balancer ingress)
- Add CI/CD image builds that publish to Artifact Registry before Terraform apply

