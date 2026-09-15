ALTER TABLE jobs_sf ADD COLUMN generation_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE jobs_sf ADD COLUMN upscale_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE jobs_sf ADD COLUMN failed_mode TEXT;
ALTER TABLE jobs_sf ADD COLUMN failure_code TEXT;
ALTER TABLE jobs_sf ADD COLUMN retryable INTEGER NOT NULL DEFAULT 0;
ALTER TABLE jobs_sf ADD COLUMN last_workflow_id TEXT;
ALTER TABLE jobs_sf ADD COLUMN last_workflow_created_at TEXT;

CREATE TABLE IF NOT EXISTS job_events_sf (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  stage TEXT,
  status TEXT,
  message TEXT,
  details_json TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_sf_reference_active
  ON jobs_sf(reference_id, type, status, created_at);

CREATE INDEX IF NOT EXISTS idx_job_events_sf_job_created
  ON job_events_sf(job_id, created_at);
