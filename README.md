# IBTrACS Mapper Monorepo

A monorepo for visualizing storm tracks from the International Best Track Archive for Climate Stewardship (IBTrACS) on a mobile-friendly web map. The archive is updated daily, and this application automatically syncs with these updates.

## Structure

```
IBTrACS-mapper/
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
- Python 3.12+ (required - see `runtime.txt` and `requirements.txt`)
- PostgreSQL (via Supabase) - *Currently configured for SQLite for local development, production uses PostgreSQL*

**Setup:**
```bash
cd backend-api
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development dependencies
uvicorn app.main:app --reload
```

### 3. Database Updater (`db-updater/`)

A Python script that runs daily to fetch the latest IBTrACS archive data and update the PostgreSQL database. Supports incremental updates by detecting the latest track point date and only adding newer data.

**Tech Stack:**
- Python 3.12+ (required)
- PostgreSQL
- Pydantic for settings and data validation
- Pandas for CSV processing

**Setup:**

1. **Create virtual environment:**
   ```bash
   cd db-updater
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development and testing
   ```

3. **Local development with Docker Compose:**
   ```bash
   # Start local PostgreSQL database
   docker-compose up -d
   
   # Set environment variable
   export USE_LOCAL_DB=true
   
   # Run the updater
   python updater.py
   ```

4. **Using a remote database:**
   ```bash
   export USE_LOCAL_DB=false
   export DB_HOST=your-db-host
   export DB_PORT=5432
   export DB_NAME=ibtracs
   export DB_USER=your-username
   export DB_PASSWORD=your-password
   
   python updater.py
   ```

5. **Run tests:**
   ```bash
   # Make sure Docker is running for database tests
   pytest tests/ -v
   ```

See `db-updater/README.md` for more detailed setup instructions.

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
- Python 3.12+ (required for `backend-api` and `db-updater`)
- Docker Desktop or Docker (required for `db-updater` local development and testing)
- Terraform 1.6+ (for infrastructure deployment)
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
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Start local database (requires Docker)
   docker-compose up -d
   
   # Set environment variable for local development
   export USE_LOCAL_DB=true
   
   # Run the updater
   python updater.py
   
   # Run tests
   pytest tests/ -v
   ```

## CI/CD

The repository uses GitHub Actions for CI/CD:

### Continuous Integration (CI)

The **CI Workflow** (`.github/workflows/ci.yml`) runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

It runs tests and linting for all components:
- **Frontend**: Runs Vitest tests and ESLint
- **Backend API**: Runs pytest tests and code quality checks (ruff, black)
- **DB Updater**: Runs pytest tests with PostgreSQL service

### Deployment

Deployments are **manual-only** and triggered via GitHub Actions UI:

- **Deploy Frontend** (`.github/workflows/deploy-frontend.yml`): Manual deployment for frontend
- **Deploy Backend API** (`.github/workflows/deploy-backend-api.yml`): Manual deployment for backend API
- **Deploy DB Updater** (`.github/workflows/deploy-db-updater.yml`): Manual deployment for database updater
- **Deploy Infrastructure** (`.github/workflows/deploy-infrastructure.yml`): Manual deployment for infrastructure (Terraform)

To trigger a deployment:
1. Go to the GitHub Actions tab
2. Select the appropriate workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Environment Variables

Each component may require environment variables. See component-specific README files or `.env.example` files for details.

### Backend API

For local development (SQLite):
- `DATABASE_PATH`: Path to SQLite database file (default: `data/storms.db`)

For production (PostgreSQL):
- Database connection settings (to be configured via Supabase)

### DB Updater

**Local Development (Docker Compose):**
- `USE_LOCAL_DB=true`: Use local Docker Compose database

**Remote Database:**
- `USE_LOCAL_DB=false`: Use remote database
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

**Data Source:**
- `IBTRACS_CSV_URL`: URL to IBTrACS CSV file (default: latest version from NOAA)

### Infrastructure

- Terraform variables for Supabase and GCP credentials
- See `infrastructure/terraform/` for specific variable requirements

## Testing

Run tests for all components:

```bash
# Frontend tests
cd frontend
npm test

# Backend API tests
cd backend-api
source venv/bin/activate  # If not already activated
pytest

# DB Updater tests (requires Docker to be running)
cd db-updater
source venv/bin/activate  # If not already activated
export USE_LOCAL_DB=true
pytest tests/ -v
```

**Note:** The DB Updater tests require Docker to be running. If Docker is not available, the database tests will be skipped automatically. The CSV parsing test does not require Docker.

The CI workflow runs all tests automatically on push and pull requests.

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

