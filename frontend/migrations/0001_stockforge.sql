CREATE TABLE IF NOT EXISTS references_sf (
  id TEXT PRIMARY KEY,
  token TEXT NOT NULL,
  r2_key TEXT NOT NULL,
  filename TEXT,
  mime_type TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  bytes INTEGER NOT NULL,
  analysis_json TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflows_sf (
  id TEXT PRIMARY KEY,
  reference_id TEXT NOT NULL,
  status TEXT NOT NULL,
  stage TEXT NOT NULL,
  progress INTEGER NOT NULL,
  message TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs_sf (
  id TEXT PRIMARY KEY,
  reference_id TEXT NOT NULL,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  stage TEXT NOT NULL,
  prompt TEXT,
  width INTEGER,
  height INTEGER,
  steps INTEGER,
  seed INTEGER,
  randomize_seed INTEGER,
  event_id TEXT,
  raw_r2_key TEXT,
  final_r2_key TEXT,
  asset_token TEXT,
  artifact_sha256 TEXT,
  result_json TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans_sf (
  reference_id TEXT PRIMARY KEY,
  plan_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
