# Terraform – Google Cloud deployment

This configuration lays the groundwork for hosting IBTrACS Mapper entirely on Google Cloud.

## Currently provisioned resources

- Required Google Cloud APIs (Run, Cloud SQL, Artifact Registry, Scheduler, etc.)
- Cloud SQL PostgreSQL instance, database, and application user (publicly accessible for now)
- Artifact Registry repository for container images
- Service accounts for the backend API and DB updater jobs
- GCS bucket dedicated to serving the frontend build artefacts

These primitives will be expanded with Cloud Run services, Cloud Scheduler jobs, HTTPS load balancers, DNS records, and more as we continue the deployment work.

## Usage

1. Ensure you have a Google Cloud project and the Terraform IAM credentials with sufficient permissions (project owner/editor is easiest for development).
2. Populate a `terraform.tfvars` file (or pass variables via CLI):

   ```hcl
   project_id        = "your-project-id"
   region            = "europe-west1"
   zone              = "europe-west1-b"
   root_domain       = "ibtracs-mapper.com"
   ```

3. Initialise and apply:

   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Next steps

- Deploy Cloud Run services for the backend API and updater job
- Configure Cloud Scheduler to trigger weekly updates
- Publish the frontend behind HTTPS via Cloud Storage + Load Balancer
- Manage custom domain + DNS records
- Secure connectivity (private IPs, Secret Manager, etc.) once the basic flow is validated

