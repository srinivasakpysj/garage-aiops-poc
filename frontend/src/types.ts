export type Incident = {
  id: string;
  source: string;
  external_event_id: string | null;
  host_name: string | null;
  title: string;
  severity: string;
  status: string;
  summary: string | null;
  assigned_team: string | null;
  detected_at: string;
  created_at: string;
  updated_at: string;
};
