# IBTrACS Database Updater

This component downloads the latest IBTrACS archive data and updates the PostgreSQL database.

## Local Development Setup

### Option 1: Use Local Docker Compose Database (Recommended)

1. **Start the local database:**
   ```bash
   docker-compose up -d
   ```

2. **Configure the database URL:**
   ```bash
   export DATABASE_URL=postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs
   ```
   Or create a `.env` file with that value.

3. **Run the updater:**
   ```bash
   python updater.py
   ```

### Option 2: Use Remote Database

1. **Set environment variables:**
   ```bash
   export DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>
   ```
   Or supply the individual components in `.env` (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

2. **Run the updater:**
   ```bash
   python updater.py
   ```

## Stopping Local Database

```bash
docker-compose down
```

To also remove the data volume:
```bash
docker-compose down -v
```

## Database Connection

- **Local (Docker Compose):** `postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs`
- **Remote:** Provided via `DATABASE_URL` (or constructed from `DB_*` variables)

