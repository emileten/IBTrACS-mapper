# IBTrACS Database Updater

This component downloads the latest IBTrACS archive data and updates the PostgreSQL database.

## Local Development Setup

### Option 1: Use Local Docker Compose Database (Recommended)

1. **Start the local database:**
   ```bash
   docker-compose up -d
   ```

2. **Set environment variable:**
   ```bash
   export USE_LOCAL_DB=true
   ```
   Or create a `.env` file:
   ```
   USE_LOCAL_DB=true
   ```

3. **Run the updater:**
   ```bash
   python updater.py
   ```

### Option 2: Use Remote Database

1. **Set environment variables:**
   ```bash
   export USE_LOCAL_DB=false
   export DB_HOST=your-db-host
   export DB_PORT=5432
   export DB_NAME=ibtracs
   export DB_USER=your-username
   export DB_PASSWORD=your-password
   ```
   Or create a `.env` file with these values.

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
- **Remote:** Constructed from `DB_*` environment variables

