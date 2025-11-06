# IBTrACS Mapper Monorepo

A monorepo for visualizing storm tracks from the International Best Track Archive for Climate Stewardship (IBTrACS) on a mobile-friendly web map. The archive is updated daily, and this application automatically syncs with these updates.

## Structure

```
ibtracs-monorepo/
├── frontend/              # React UI application
├── backend-api/           # FastAPI backend service
├── db-updater/            # Database update job
├── infrastructure/        # Terraform infrastructure as code
└── .github/workflows/     # CI/CD workflows
```

## Components

### 1. Frontend (`frontend/`)

A React application built with Vite that provides a mobile-friendly web map interface for visualizing IBTrACS storm tracks.

**Tech Stack:**
- React 18
- Vite
- Leaflet & React-Leaflet for mapping
- Vitest for testing

**Setup:**
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend API (`backend-api/`)

A FastAPI service that provides REST endpoints for querying storm track data from the database.

**Tech Stack:**
- FastAPI
- Python 3.12+ (required - see requirements.txt)
- PostgreSQL (via Supabase) - *Currently configured for SQLite, migration in progress*

**Setup:**
```bash
cd backend-api
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Database Updater (`db-updater/`)

A Python script that runs daily to fetch the latest IBTrACS archive data and update the database.

**Setup:**
```bash
cd db-updater
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python updater.py
```

### 4. Infrastructure (`infrastructure/`)

Terraform configurations for managing cloud infrastructure:
- Supabase for database hosting
- GCP for application hosting (Cloud Run, Cloud Storage, Cloud Scheduler)

**Setup:**
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

## Development

### Prerequisites

- Node.js 18+
- Python 3.12+ (required for backend-api)
- Terraform 1.6+
- Git

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd IBTrACS-mapper
   ```

2. **Set up Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Set up Backend API:**
   ```bash
   cd backend-api
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Set up Database Updater:**
   ```bash
   cd db-updater
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Configure environment variables
   python updater.py
   ```

## CI/CD

The repository uses GitHub Actions for CI/CD:

- **CI Workflow** (`.github/workflows/ci.yml`): Runs tests and linting on all components
- **Deploy All** (`.github/workflows/deploy-all.yml`): Orchestrates deployment of all components
- **Component-specific workflows**: Each component has its own deployment workflow in its `.github/workflows/` directory

### Path-based Triggers

Workflows are triggered based on file paths:
- Changes to `frontend/**` → Deploy frontend
- Changes to `backend-api/**` → Deploy API
- Changes to `db-updater/**` → Deploy updater
- Changes to `infrastructure/**` → Run Terraform

## Environment Variables

Each component may require environment variables. See component-specific README files or `.env.example` files for details.

### Backend API
- Database connection settings (currently SQLite, migrating to Supabase/PostgreSQL)

### DB Updater
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- IBTrACS archive source URL

### Infrastructure
- Terraform variables for Supabase and GCP credentials

## Testing

Run tests for all components:

```bash
# Frontend tests
cd frontend && npm test

# Backend API tests
cd backend-api && pytest

# All tests (from root)
# CI workflow runs all tests automatically
```

## Deployment

Deployments are handled via GitHub Actions workflows. Manual deployments can be triggered via workflow_dispatch events.

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

