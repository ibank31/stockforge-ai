"""SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .artifact import Artifact
from .asset import Asset
from .execution_record import GenerationExecutionRecord
from .provenance import ArtifactLineage, ProvenanceRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, path TEXT NOT NULL UNIQUE, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL, asset_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'registered', relative_path TEXT, mime_type TEXT, size_bytes INTEGER, checksum_sha256 TEXT, source TEXT NOT NULL DEFAULT 'manual', metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, UNIQUE(project_id, relative_path), UNIQUE(project_id, name));
CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL, relative_path TEXT NOT NULL, mime_type TEXT, size_bytes INTEGER NOT NULL, sha256 TEXT NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, UNIQUE(project_id, relative_path), UNIQUE(project_id, sha256));
CREATE TABLE IF NOT EXISTS generation_executions (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, operation TEXT NOT NULL, state TEXT NOT NULL, job_id TEXT, provider_id TEXT, provider_job_id TEXT, pipeline_id TEXT, pipeline_version INTEGER, step_id TEXT, plugin_id TEXT, plugin_version TEXT, model_id TEXT, model_version TEXT, workflow_hash TEXT, prompt_hash TEXT, artifact_ids_json TEXT NOT NULL DEFAULT '[]', input_artifact_ids_json TEXT NOT NULL DEFAULT '[]', parameters_json TEXT NOT NULL DEFAULT '{}', error_code TEXT, error_message TEXT, schema_version INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS provenance_records (id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, project_id TEXT NOT NULL, operation TEXT NOT NULL, job_id TEXT, execution_id TEXT, pipeline_id TEXT, pipeline_version INTEGER, pipeline_hash TEXT, step_id TEXT, plugin_id TEXT, plugin_version TEXT, model_id TEXT, model_version TEXT, model_hash TEXT, workflow_hash TEXT, prompt_hash TEXT, input_artifact_ids_json TEXT NOT NULL DEFAULT '[]', parameters_json TEXT NOT NULL DEFAULT '{}', metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, schema_version INTEGER NOT NULL, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS artifact_lineage (id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, parent_artifact_id TEXT NOT NULL, project_id TEXT NOT NULL, relation TEXT NOT NULL, execution_id TEXT, sequence INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, schema_version INTEGER NOT NULL, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE, FOREIGN KEY (parent_artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE, UNIQUE(artifact_id, parent_artifact_id, relation));
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id); CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status); CREATE INDEX IF NOT EXISTS idx_assets_checksum ON assets(checksum_sha256); CREATE INDEX IF NOT EXISTS idx_artifacts_project_id ON artifacts(project_id); CREATE INDEX IF NOT EXISTS idx_artifacts_sha256 ON artifacts(sha256); CREATE INDEX IF NOT EXISTS idx_execution_project_id ON generation_executions(project_id); CREATE INDEX IF NOT EXISTS idx_execution_provider_job ON generation_executions(provider_job_id); CREATE INDEX IF NOT EXISTS idx_execution_state ON generation_executions(state); CREATE INDEX IF NOT EXISTS idx_provenance_artifact ON provenance_records(artifact_id); CREATE INDEX IF NOT EXISTS idx_provenance_execution ON provenance_records(execution_id); CREATE INDEX IF NOT EXISTS idx_lineage_artifact ON artifact_lineage(artifact_id); CREATE INDEX IF NOT EXISTS idx_lineage_parent ON artifact_lineage(parent_artifact_id);
"""

class Database:
    """Small SQLite wrapper used by the StockForge core."""
    def __init__(self, path: Path) -> None: self.path = Path(path)
    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True); conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row; conn.execute("PRAGMA foreign_keys = ON"); return conn
    def initialize(self) -> None:
        with self.connect() as conn: conn.executescript(SCHEMA)
    def create_project(self, project_id: str, name: str, project_path: Path) -> dict:
        with self.connect() as conn: conn.execute("INSERT INTO projects (id, name, path) VALUES (?, ?, ?)", (project_id, name, str(project_path)))
        return {"id": project_id, "name": name, "path": str(project_path), "status": "active"}
    def list_projects(self) -> list[dict]:
        with self.connect() as conn: rows = conn.execute("SELECT id, name, path, status, created_at, updated_at FROM projects ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]
    def create_asset(self, asset: Asset) -> Asset:
        r=asset.to_record()
        with self.connect() as c: c.execute("INSERT INTO assets (id,project_id,name,asset_type,status,relative_path,mime_type,size_bytes,checksum_sha256,source,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (r["id"],r["project_id"],r["name"],r["asset_type"],r["status"],r["relative_path"],r["mime_type"],r["size_bytes"],r["checksum_sha256"],r["source"],json.dumps(r["metadata"],ensure_ascii=False,sort_keys=True))); row=c.execute("SELECT * FROM assets WHERE id=?",(asset.id,)).fetchone()
        return self._asset_from_row(row)
    def list_assets(self, project_id: str | None = None) -> list[Asset]:
        with self.connect() as c: rows=c.execute("SELECT * FROM assets WHERE project_id=? ORDER BY created_at DESC",(project_id,)).fetchall() if project_id else c.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall()
        return [self._asset_from_row(r) for r in rows]
    def create_artifact(self, artifact: Artifact) -> Artifact:
        r=artifact.to_dict()
        with self.connect() as c: c.execute("INSERT INTO artifacts (id,project_id,kind,relative_path,mime_type,size_bytes,sha256,metadata_json) VALUES (?,?,?,?,?,?,?,?)",(r["id"],r["project_id"],r["kind"],r["relative_path"],r["mime_type"],r["size_bytes"],r["sha256"],json.dumps(r["metadata"],ensure_ascii=False,sort_keys=True)))
        return artifact
    def create_artifacts_and_execution(self, artifacts: tuple[Artifact,...], execution: GenerationExecutionRecord) -> tuple[tuple[Artifact,...],GenerationExecutionRecord]:
        actual=[]
        with self.connect() as c:
            for artifact in artifacts:
                r=artifact.to_dict(); existing=c.execute("SELECT * FROM artifacts WHERE project_id=? AND sha256=?",(r["project_id"],r["sha256"])).fetchone()
                if existing is not None: actual.append(self._artifact_from_row(existing)); continue
                collision=c.execute("SELECT id FROM artifacts WHERE project_id=? AND relative_path=?",(r["project_id"],r["relative_path"])).fetchone()
                if collision is not None: raise sqlite3.IntegrityError(f"Artifact relative path already belongs to a different artifact: {r['relative_path']}")
                c.execute("INSERT INTO artifacts (id,project_id,kind,relative_path,mime_type,size_bytes,sha256,metadata_json) VALUES (?,?,?,?,?,?,?,?)",(r["id"],r["project_id"],r["kind"],r["relative_path"],r["mime_type"],r["size_bytes"],r["sha256"],json.dumps(r["metadata"],ensure_ascii=False,sort_keys=True))); actual.append(artifact)
            d=execution.to_dict(); d["artifact_ids"]=[a.id for a in actual]; final=GenerationExecutionRecord.from_dict(d)
            existing_execution=c.execute("SELECT 1 FROM generation_executions WHERE id=?",(final.id,)).fetchone()
            if existing_execution is None: self._insert_execution(c,final)
            else: self._update_execution_connection(c,final)
        return tuple(actual),final
    def create_execution(self, record: GenerationExecutionRecord) -> GenerationExecutionRecord:
        with self.connect() as c: self._insert_execution(c,record)
        return record
    def update_execution(self, record: GenerationExecutionRecord) -> GenerationExecutionRecord:
        with self.connect() as c: self._update_execution_connection(c,record)
        return record
    def create_provenance(self, record: ProvenanceRecord) -> ProvenanceRecord:
        d=record.to_dict()
        with self.connect() as c: c.execute("INSERT INTO provenance_records (id,artifact_id,project_id,operation,job_id,execution_id,pipeline_id,pipeline_version,pipeline_hash,step_id,plugin_id,plugin_version,model_id,model_version,model_hash,workflow_hash,prompt_hash,input_artifact_ids_json,parameters_json,metadata_json,created_at,schema_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(d["id"],d["artifact_id"],d["project_id"],d["operation"],d["job_id"],d["execution_id"],d["pipeline_id"],d["pipeline_version"],d["pipeline_hash"],d["step_id"],d["plugin_id"],d["plugin_version"],d["model_id"],d["model_version"],d["model_hash"],d["workflow_hash"],d["prompt_hash"],json.dumps(d["input_artifact_ids"],sort_keys=True),json.dumps(d["parameters"],ensure_ascii=False,sort_keys=True),json.dumps(d["metadata"],ensure_ascii=False,sort_keys=True),d["created_at"],d["schema_version"]))
        return record
    def get_provenance(self, provenance_id: str) -> ProvenanceRecord | None:
        with self.connect() as c: row=c.execute("SELECT * FROM provenance_records WHERE id=?",(provenance_id,)).fetchone()
        return self._provenance_from_row(row) if row else None
    def list_provenance(self, artifact_id: str | None = None) -> list[ProvenanceRecord]:
        with self.connect() as c: rows=c.execute("SELECT * FROM provenance_records WHERE artifact_id=? ORDER BY created_at,id",(artifact_id,)).fetchall() if artifact_id else c.execute("SELECT * FROM provenance_records ORDER BY created_at,id").fetchall()
        return [self._provenance_from_row(r) for r in rows]
    def create_lineage(self, lineage: ArtifactLineage) -> ArtifactLineage:
        d=lineage.to_dict()
        with self.connect() as c: c.execute("INSERT INTO artifact_lineage (id,artifact_id,parent_artifact_id,project_id,relation,execution_id,sequence,created_at,schema_version) VALUES (?,?,?,?,?,?,?,?,?)",(d["id"],d["artifact_id"],d["parent_artifact_id"],d["project_id"],d["relation"],d["execution_id"],d["sequence"],d["created_at"],d["schema_version"]))
        return lineage
    def list_lineage(self, artifact_id: str | None = None, parent_artifact_id: str | None = None) -> list[ArtifactLineage]:
        with self.connect() as c:
            if artifact_id is not None: rows=c.execute("SELECT * FROM artifact_lineage WHERE artifact_id=? ORDER BY sequence,id",(artifact_id,)).fetchall()
            elif parent_artifact_id is not None: rows=c.execute("SELECT * FROM artifact_lineage WHERE parent_artifact_id=? ORDER BY sequence,id",(parent_artifact_id,)).fetchall()
            else: rows=c.execute("SELECT * FROM artifact_lineage ORDER BY created_at,id").fetchall()
        return [self._lineage_from_row(r) for r in rows]
    @staticmethod
    def _update_execution_connection(c: sqlite3.Connection, record: GenerationExecutionRecord) -> None:
        d=record.to_dict(); updated=c.execute("UPDATE generation_executions SET project_id=?,operation=?,state=?,job_id=?,provider_id=?,provider_job_id=?,pipeline_id=?,pipeline_version=?,step_id=?,plugin_id=?,plugin_version=?,model_id=?,model_version=?,workflow_hash=?,prompt_hash=?,artifact_ids_json=?,input_artifact_ids_json=?,parameters_json=?,error_code=?,error_message=?,schema_version=? WHERE id=?",(d["project_id"],d["operation"],d["state"],d["job_id"],d["provider_id"],d["provider_job_id"],d["pipeline_id"],d["pipeline_version"],d["step_id"],d["plugin_id"],d["plugin_version"],d["model_id"],d["model_version"],d["workflow_hash"],d["prompt_hash"],json.dumps(d["artifact_ids"],sort_keys=True),json.dumps(d["input_artifact_ids"],sort_keys=True),json.dumps(d["parameters"],ensure_ascii=False,sort_keys=True),d["error_code"],d["error_message"],d["schema_version"],record.id))
        if updated.rowcount != 1: raise KeyError(f"Execution not found: {record.id}")
    @staticmethod
    def _insert_execution(c: sqlite3.Connection, record: GenerationExecutionRecord) -> None:
        d=record.to_dict(); c.execute("INSERT INTO generation_executions (id,project_id,operation,state,job_id,provider_id,provider_job_id,pipeline_id,pipeline_version,step_id,plugin_id,plugin_version,model_id,model_version,workflow_hash,prompt_hash,artifact_ids_json,input_artifact_ids_json,parameters_json,error_code,error_message,schema_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(d["id"],d["project_id"],d["operation"],d["state"],d["job_id"],d["provider_id"],d["provider_job_id"],d["pipeline_id"],d["pipeline_version"],d["step_id"],d["plugin_id"],d["plugin_version"],d["model_id"],d["model_version"],d["workflow_hash"],d["prompt_hash"],json.dumps(d["artifact_ids"],sort_keys=True),json.dumps(d["input_artifact_ids"],sort_keys=True),json.dumps(d["parameters"],ensure_ascii=False,sort_keys=True),d["error_code"],d["error_message"],d["schema_version"]))
    def get_artifact(self, artifact_id: str) -> Artifact | None:
        with self.connect() as c: row=c.execute("SELECT * FROM artifacts WHERE id=?",(artifact_id,)).fetchone()
        return self._artifact_from_row(row) if row else None
    def list_artifacts(self, project_id: str | None = None) -> list[Artifact]:
        with self.connect() as c: rows=c.execute("SELECT * FROM artifacts WHERE project_id=? ORDER BY created_at DESC",(project_id,)).fetchall() if project_id else c.execute("SELECT * FROM artifacts ORDER BY created_at DESC").fetchall()
        return [self._artifact_from_row(r) for r in rows]
    def get_execution(self, execution_id: str) -> GenerationExecutionRecord | None:
        with self.connect() as c: row=c.execute("SELECT * FROM generation_executions WHERE id=?",(execution_id,)).fetchone()
        return self._execution_from_row(row) if row else None
    @staticmethod
    def _asset_from_row(row: sqlite3.Row) -> Asset:
        d=dict(row); d["metadata"]=json.loads(d.pop("metadata_json")); return Asset.from_record(d)
    @staticmethod
    def _artifact_from_row(row: sqlite3.Row) -> Artifact:
        d=dict(row); d.pop("created_at",None); d["metadata"]=json.loads(d.pop("metadata_json")); d["schema_version"]=1; return Artifact.from_dict(d)
    @staticmethod
    def _execution_from_row(row: sqlite3.Row) -> GenerationExecutionRecord:
        d=dict(row); d["artifact_ids"]=json.loads(d.pop("artifact_ids_json")); d["input_artifact_ids"]=json.loads(d.pop("input_artifact_ids_json")); d["parameters"]=json.loads(d.pop("parameters_json")); d.pop("created_at",None); return GenerationExecutionRecord.from_dict(d)
    @staticmethod
    def _provenance_from_row(row: sqlite3.Row) -> ProvenanceRecord:
        d=dict(row); d["input_artifact_ids"]=json.loads(d.pop("input_artifact_ids_json")); d["parameters"]=json.loads(d.pop("parameters_json")); d["metadata"]=json.loads(d.pop("metadata_json")); return ProvenanceRecord.from_dict(d)
    @staticmethod
    def _lineage_from_row(row: sqlite3.Row) -> ArtifactLineage:
        return ArtifactLineage(**dict(row))
