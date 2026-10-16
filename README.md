# Garage AIOps POC
React + TypeScript + Vite frontend, FastAPI backend, PostgreSQL persistence.

**POC data warning:** Seed records are illustrative. Zabbix, Teams, email, and real AI integrations are not connected. AI guidance is rule-based and advisory; no remediation is executed.

## RHEL 9 native deployment
Prerequisites: PostgreSQL 16, Python 3.11, Node.js 22, Nginx installed.

1. Create database/role in PostgreSQL and configure `backend/.env` using `.env.example`. Use a URL-encoded DB password and never commit `.env`.
2. Backend:
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit DATABASE_URL
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
3. Frontend in a second terminal:
```bash
cd frontend
npm install
npm run build
sudo mkdir -p /var/www/garage-aiops
sudo cp -r dist/. /var/www/garage-aiops/
sudo chown -R nginx:nginx /var/www/garage-aiops
```
4. Configure Nginx:
```bash
sudo cp deploy/nginx/garage-aiops.conf /etc/nginx/conf.d/garage-aiops.conf
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```
If Nginx warns of a duplicate catch-all server on port 80, inspect `/etc/nginx/conf.d/` and disable the duplicate default server block before reloading.
5. Keep FastAPI bound to 127.0.0.1. Do not expose ports 8000 or 5432. Restrict port 80 to your office public IP for initial testing, and configure TLS/authentication before wider use.

API: `/health`, `/api/v1/dashboard/summary`, `/api/v1/servers`, `/api/v1/incidents`, `/api/v1/activity`, `/api/v1/insights/current`.
