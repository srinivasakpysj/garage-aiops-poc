# GARAGE AIOps — Phase 1 Dashboard + API

Responsive GARAGE AIOps dashboard modeled on the supplied reference: dark navigation rail, global search, five KPI cards, health donut, incident charts, filterable incident table, AI insights tabs, recent activity, connected systems, inventory, teams, runbooks, settings and audit history. The dashboard is integrated with a persistent FastAPI/PostgreSQL backend using SQLAlchemy 2 and Alembic.

## Run
1. Copy `.env.example` to `.env`.
2. Set a strong `POSTGRES_PASSWORD` and update the password in `DATABASE_URL` if running outside Compose.
3. Run `docker compose up --build -d`.
4. Dashboard: http://localhost:5173
5. Swagger API: http://localhost:8000/docs
6. Readiness: http://localhost:8000/health/ready

The API container applies Alembic migrations and seeds a demo inventory only if the database is empty. Demo records persist in PostgreSQL, not browser state.

## Tests
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```
Tests use isolated SQLite.

## API highlights
- `GET /api/v1/dashboard/overview?window=24h`
- `GET /api/v1/servers`, `GET /api/v1/teams`
- `GET /api/v1/incidents?q=&severity=&status=&limit=&offset=`
- `PATCH /api/v1/incidents/{id}/status`
- `GET /api/v1/incidents/{id}/events`
- `GET /api/v1/ai-analyses`, `GET /api/v1/recommendations`
- `PATCH /api/v1/recommendations/{id}/status`
- `GET /api/v1/notifications`, `PATCH /api/v1/notifications/{id}/read`
- `GET /api/v1/audit-logs`, `GET /api/v1/integrations`

## Dashboard interactions
- Sidebar items scroll to their corresponding operational sections.
- Global search and incident filters narrow the incident table.
- Time-window controls refresh dashboard metrics from the API.
- Incident action menus open details, acknowledge, start work, or resolve; updates are saved to PostgreSQL and audited.
- AI insight tabs switch between analysis, metrics, and recommendations.
- Recommendation actions and notification read actions call the backend.
- Demo records are clearly seeded into PostgreSQL; the frontend does not use browser state as its permanent datastore.

## Important
Zabbix, external AI, Teams, and email are reported as not configured until real credentials/connectors are implemented. AI suggestions are advisory; no remediation commands run. Add authentication/SSO, RBAC, TLS, rate limiting, secrets management, and operational backups before public or production deployment.
