import { useEffect, useState } from "react";
import { getIncidents } from "./api/incidents";
import type { Incident } from "./types";

const demoCards = [
  { label: "Monitoring sources", value: "Zabbix 7.2", note: "Integration not connected", icon: "◉" },
  { label: "Managed servers", value: "—", note: "Will populate from inventory sync", icon: "▣" },
  { label: "Open incidents", value: "—", note: "Loaded from the API below", icon: "△" },
  { label: "AI triage", value: "Planned", note: "Recommendations require integration", icon: "✳" },
];

function pretty(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getIncidents()
      .then(setIncidents)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Could not load incidents"))
      .finally(() => setLoading(false));
  }, []);

  const openCount = incidents.filter((item) => !["resolved"].includes(item.status)).length;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">G</div><div><strong>GARAGE</strong><span>AIOps platform</span></div></div>
        <div className="nav-caption">WORKSPACE</div>
        <nav>
          <a className="active" href="#overview"><span>▦</span> Overview</a>
          <a href="#incidents"><span>◈</span> Incidents</a>
          <a href="#servers"><span>▣</span> Server inventory</a>
          <a href="#integrations"><span>⌘</span> Integrations</a>
        </nav>
        <div className="sidebar-bottom"><div className="status-dot" /> Local development <small>POC foundation · v0.1.0</small></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div><span className="eyebrow">INFRASTRUCTURE OPERATIONS</span><h1>Overview</h1></div><div className="top-actions"><span className="env-pill">LOCAL POC</span><div className="avatar">GK</div></div></header>
        <section className="welcome">
          <div><span className="eyebrow light">DETECT. UNDERSTAND. RESOLVE. IMPROVE.</span><h2>Infrastructure health, at a glance.</h2><p>A single operational view for monitoring events, incident ownership and guided troubleshooting.</p></div>
          <div className="welcome-symbol">✳</div>
        </section>
        <section className="metrics-grid">
          {demoCards.map((card) => <article className="metric-card" key={card.label}><div className="metric-head"><span>{card.label}</span><span className="metric-icon">{card.icon}</span></div><strong className="metric-value">{card.label === "Open incidents" && !loading && !error ? openCount : card.value}</strong><p>{card.note}</p></article>)}
        </section>
        <section className="content-card" id="incidents">
          <div className="section-heading"><div><h3>Recent incidents</h3><p>Incident records returned by the FastAPI backend</p></div><span className="count-pill">{incidents.length} records</span></div>
          {loading && <div className="empty-state">Loading incidents from the API…</div>}
          {error && <div className="error-state"><strong>API connection unavailable</strong><p>{error}</p><span>Start the FastAPI backend on port 8000, then refresh this page.</span></div>}
          {!loading && !error && incidents.length === 0 && <div className="empty-state"><div className="empty-icon">◈</div><strong>No incidents yet</strong><p>Create a synthetic test incident using the API instructions in README.md. Zabbix ingestion will be added in a later increment.</p></div>}
          {!loading && !error && incidents.length > 0 && <div className="table-wrap"><table><thead><tr><th>Incident</th><th>Host</th><th>Severity</th><th>Status</th><th>Assigned team</th></tr></thead><tbody>{incidents.map((incident) => <tr key={incident.id}><td><strong>{incident.title}</strong><small>{incident.source} · {new Date(incident.created_at).toLocaleString()}</small></td><td>{incident.host_name ?? "—"}</td><td><span className={`severity severity-${incident.severity}`}>{pretty(incident.severity)}</span></td><td>{pretty(incident.status)}</td><td>{incident.assigned_team ?? "Unassigned"}</td></tr>)}</tbody></table></div>}
        </section>
        <section className="bottom-grid">
          <article className="content-card" id="integrations"><div className="section-heading"><div><h3>Integration readiness</h3><p>Planned connections for the POC</p></div></div><div className="integration-row"><span className="integration-icon zabbix">Z</span><div><strong>Zabbix 7.2</strong><small>Webhook and read-only API client</small></div><span className="state planned">Planned</span></div><div className="integration-row"><span className="integration-icon teams">T</span><div><strong>Microsoft Teams</strong><small>Incident assignment notifications</small></div><span className="state planned">Planned</span></div><div className="integration-row"><span className="integration-icon email">✉</span><div><strong>Email</strong><small>Delivery, retries and follow-ups</small></div><span className="state planned">Planned</span></div></article>
          <article className="content-card" id="servers"><div className="section-heading"><div><h3>POC rollout</h3><p>Controlled validation before scaling</p></div></div><div className="rollout-number">5–10 <span>pilot servers</span></div><div className="progress-track"><div className="progress-fill" /></div><div className="rollout-footer"><span>Foundation increment</span><strong>In progress</strong></div><p className="muted-copy">Validate event ingestion, routing, acknowledgement and recovery verification before expanding toward the 350-server environment.</p></article>
        </section>
        <footer>Garage AIOps · POC starter · No live monitoring integrations are connected yet.</footer>
      </main>
    </div>
  );
}
