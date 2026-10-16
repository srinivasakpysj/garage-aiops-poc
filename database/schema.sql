-- Reference schema for PostgreSQL 16. SQLAlchemy models in backend/app/models/entities.py
-- are the executable starter definitions. Apply reviewed migrations in shared environments.
CREATE TABLE servers (
  id varchar(36) PRIMARY KEY,
  external_host_id varchar(128) UNIQUE,
  hostname varchar(255) NOT NULL,
  environment varchar(50) NOT NULL DEFAULT 'unknown',
  team_name varchar(120),
  criticality varchar(30) NOT NULL DEFAULT 'non_critical',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE incidents (
  id varchar(36) PRIMARY KEY,
  source varchar(40) NOT NULL DEFAULT 'manual',
  external_event_id varchar(128),
  server_id varchar(36) REFERENCES servers(id),
  host_name varchar(255),
  title varchar(255) NOT NULL,
  severity varchar(20) NOT NULL DEFAULT 'warning',
  status varchar(30) NOT NULL DEFAULT 'open',
  summary text,
  assigned_team varchar(120),
  detected_at timestamptz NOT NULL DEFAULT now(),
  acknowledged_at timestamptz,
  resolved_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_incident_source_event UNIQUE(source, external_event_id)
);
CREATE INDEX ix_incidents_status ON incidents(status);
CREATE INDEX ix_incidents_severity ON incidents(severity);
CREATE INDEX ix_incidents_created_at ON incidents(created_at DESC);

CREATE TABLE ai_analyses (
  id varchar(36) PRIMARY KEY,
  incident_id varchar(36) NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  model_name varchar(120) NOT NULL,
  facts jsonb NOT NULL DEFAULT '{}'::jsonb,
  hypotheses jsonb NOT NULL DEFAULT '[]'::jsonb,
  recommended_actions jsonb NOT NULL DEFAULT '[]'::jsonb,
  confidence varchar(30),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE notifications (
  id varchar(36) PRIMARY KEY,
  incident_id varchar(36) NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  channel varchar(30) NOT NULL,
  recipient varchar(255) NOT NULL,
  status varchar(30) NOT NULL DEFAULT 'pending',
  provider_message_id varchar(255),
  error_detail text,
  attempt_count integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  sent_at timestamptz
);

CREATE TABLE audit_events (
  id varchar(36) PRIMARY KEY,
  actor varchar(255) NOT NULL DEFAULT 'system',
  action varchar(120) NOT NULL,
  entity_type varchar(80) NOT NULL,
  entity_id varchar(36) NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
