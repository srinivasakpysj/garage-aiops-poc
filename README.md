# Garage AIOps — POC Starter

A local-first foundation for a 30-day infrastructure-operations POC. This first increment provides:
- React + TypeScript dashboard shell
- FastAPI API with health, incident-list, and incident-create endpoints
- SQLAlchemy models for servers, incidents, AI analyses, notifications, and audit events
- PostgreSQL via Docker Compose
- Pytest API tests using SQLite
- No real Zabbix, Teams, email, or AI credentials required yet

## Prerequisites (Windows)
1. Install Git.
2. Install Python 3.11+ (3.12 recommended).
3. Install Node.js LTS (includes npm).
4. Install Docker Desktop and start it.
5. Install VS Code and extensions: Python, Pylance, ESLint, Docker.

## Start PostgreSQL
From the repository root:
```powershell
docker compose up -d db
docker compose ps
```
PostgreSQL is available locally at `localhost:5432` using the development-only credentials in `.env.example`. Do not reuse these credentials outside local development.

## Start the FastAPI backend
Open a VS Code terminal at the repository root:
```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item ..\.env.example .env
uvicorn app.main:app --reload
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again.

Open:
- API health: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs

The API creates missing tables on startup for this starter increment. Before production, replace this convenience with Alembic migrations and reviewed deployment migrations.

## Start the frontend
In a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open the local URL printed by Vite (normally http://localhost:5173). The Vite development server proxies `/api` requests to FastAPI.

## Run backend tests
From the repository root:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Try the API
Create an incident:
```powershell
$body = @{
  source = "manual"
  title = "POC: high memory usage"
  severity = "high"
  status = "open"
  summary = "Example incident created during local testing."
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/incidents -ContentType "application/json" -Body $body
```
List incidents:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/incidents
```

## Repository map
```text
garage-aiops-poc/
  backend/
    app/
      api/routes/       # HTTP endpoints
      core/              # settings
      db/                # database session
      models/            # SQLAlchemy entities
      schemas/           # request/response validation
      main.py
    tests/
    requirements.txt
  frontend/
    src/
      api/
      components/
      pages/
      types/
    index.html
    package.json
    vite.config.ts
  database/
    schema.sql           # reference PostgreSQL schema
  docs/
    architecture.md
    zabbix-integration.md
  docker-compose.yml
  .env.example
```

## Current increment boundaries
Implemented: local dashboard shell, API health, basic incident list/create, database entities, and tests.

Not implemented yet: Zabbix webhook authentication and event ingestion, queue/worker, live metrics, AI model calls, Teams/SMTP delivery, RBAC, production migrations, AWS deployment, and automated remediation.

## Integration design decisions
- Zabbix 7.2 is the monitoring system of record. Integrate using a dedicated, least-privilege API identity and a webhook/action for events.
- Make incoming Zabbix events idempotent using the Zabbix event ID before enabling ingestion.
- Keep outbound Teams/email behind notification-provider interfaces and retry safely.
- Validate AI output against a strict schema; label facts separately from hypotheses and never execute suggested commands automatically.
- Keep the Zabbix API/database private. Use TLS, secrets management, IAM roles, audit trails, and role-based access before production use.
- Verify whether Zabbix is on-premises or in AWS before selecting network connectivity and deployment topology.
